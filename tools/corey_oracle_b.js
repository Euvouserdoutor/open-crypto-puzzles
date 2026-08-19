#!/usr/bin/env node
"use strict";

/*
 * Independent single-candidate validation path for the Corey Phillips puzzle.
 *
 * This file intentionally has no candidate generator, input stream, wordlist,
 * concurrency, network, signing, or transaction functionality. It does not
 * import or translate tools/corey_oracle.py.
 */

const crypto = require("node:crypto");
const fs = require("node:fs");
const pathModule = require("node:path");

const TARGET = "bc1qcyrndzgy036f6ax370g8zyvlw86ulawgt0246r";
const TARGET_PROGRAM = "c1073689047c749d74d1f3d071119f71f5cff5c8";
const DEFAULT_PATH = "m/84'/0'/0'/0/0";
const SISTER = "bc1q57euh23y3qs2f9d5mtwpax5lqecfvrdkqce82a";
const IMAGE_RELATIVE = "2-mid-prizes/corey-phillips-kitten-passphrase-1msats/clues/kitten.jpeg";
const IMAGE_SHA256 = "b988e0881a0211222e83f3e2a4bfac695c951bf96aa33ec112fab6992f5e7343";
const ENTROPY_HEX = "1808d35318ac7cb98b69ff9779b699d6a631f15e0b353ac89b7c4020774832ed";
const WORD_INDICES = [
  192, 564, 1702, 394, 1598, 742, 365, 511, 1211, 1645, 1331, 1386,
  792, 1989, 961, 821, 470, 550, 1784, 1026, 59, 1312, 1629, 1503,
];
const WORDS = [
  "blossom", "educate", "state", "course", "sick", "fresh", "color",
  "divide", "number", "soap", "please", "pull", "glide", "weather",
  "join", "grit", "depart", "dynamic", "tenant", "leopard", "alter",
  "piano", "slight", "room",
];
const MNEMONIC = WORDS.join(" ");
const CURVE_N = BigInt("0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141");
const BECH32_ALPHABET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l";

class ValidationError extends Error {}

function sha256(data) {
  return crypto.createHash("sha256").update(data).digest();
}

function hmac512(key, data) {
  return crypto.createHmac("sha512", key).update(data).digest();
}

function normalizeText(value, mode = "standard") {
  if (typeof value !== "string") throw new ValidationError("text must be a Unicode string");
  if (mode === "standard") return value.normalize("NFKD");
  if (mode === "raw-compat") return value;
  throw new ValidationError(`unsupported normalization mode: ${mode}`);
}

function normalizedBytes(value, mode = "standard") {
  return Buffer.from(normalizeText(value, mode), "utf8");
}

function bip39Seed(mnemonic, passphrase, mode = "standard") {
  const password = normalizedBytes(mnemonic, mode);
  const salt = Buffer.concat([Buffer.from("mnemonic", "ascii"), normalizedBytes(passphrase, mode)]);
  return crypto.pbkdf2Sync(password, salt, 2048, 64, "sha512");
}

function bufferToBigInt(buffer) {
  return BigInt(`0x${buffer.toString("hex") || "0"}`);
}

function bigIntTo32(value) {
  if (value < 0n || value >= (1n << 256n)) throw new ValidationError("integer does not fit 32 bytes");
  return Buffer.from(value.toString(16).padStart(64, "0"), "hex");
}

function compressedPublicKey(privateKey) {
  if (privateKey <= 0n || privateKey >= CURVE_N) throw new ValidationError("invalid secp256k1 scalar");
  try {
    const ecdh = crypto.createECDH("secp256k1");
    ecdh.setPrivateKey(bigIntTo32(privateKey));
    return ecdh.getPublicKey(null, "compressed");
  } catch (error) {
    throw new ValidationError(`secp256k1 failure: ${error.message}`);
  }
}

function hash160(data) {
  return crypto.createHash("ripemd160").update(sha256(data)).digest();
}

function masterFromSeed(seed) {
  const digest = hmac512(Buffer.from("Bitcoin seed", "ascii"), seed);
  const key = bufferToBigInt(digest.subarray(0, 32));
  if (key <= 0n || key >= CURVE_N) throw new ValidationError("invalid BIP32 master key");
  return { key, chain: digest.subarray(32) };
}

function ckdPrivate(parentKey, parentChain, index) {
  if (!Number.isInteger(index) || index < 0 || index > 0xffffffff) {
    throw new ValidationError("BIP32 child index out of range");
  }
  const indexBytes = Buffer.alloc(4);
  indexBytes.writeUInt32BE(index);
  const head = index >= 0x80000000
    ? Buffer.concat([Buffer.from([0]), bigIntTo32(parentKey)])
    : compressedPublicKey(parentKey);
  const digest = hmac512(parentChain, Buffer.concat([head, indexBytes]));
  const left = bufferToBigInt(digest.subarray(0, 32));
  const child = (left + parentKey) % CURVE_N;
  if (left >= CURVE_N || child === 0n) throw new ValidationError("invalid BIP32 child");
  return { key: child, chain: digest.subarray(32) };
}

function parsePath(path) {
  if (typeof path !== "string") throw new ValidationError("path must be a string");
  const parts = path.split("/");
  if (parts.shift() !== "m") throw new ValidationError("path must start with m");
  return parts.map((part) => {
    const hardened = /['hH]$/.test(part);
    const digits = hardened ? part.slice(0, -1) : part;
    if (!/^(0|[1-9][0-9]*)$/.test(digits)) throw new ValidationError(`invalid path component: ${part}`);
    const value = Number(digits);
    if (!Number.isSafeInteger(value) || value >= 0x80000000) throw new ValidationError("path component too large");
    return value + (hardened ? 0x80000000 : 0);
  });
}

function derivePrivatePath(seed, path = DEFAULT_PATH) {
  const master = masterFromSeed(seed);
  let node = master;
  for (const index of parsePath(path)) node = ckdPrivate(node.key, node.chain, index);
  return { master, child: node };
}

function polymod(values) {
  const generators = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3];
  let checksum = 1;
  for (const value of values) {
    const top = checksum >>> 25;
    checksum = ((checksum & 0x1ffffff) << 5) ^ value;
    for (let bit = 0; bit < 5; bit += 1) {
      if ((top >>> bit) & 1) checksum ^= generators[bit];
    }
    checksum >>>= 0;
  }
  return checksum >>> 0;
}

function hrpExpand(hrp) {
  return [...hrp].map((c) => c.charCodeAt(0) >>> 5)
    .concat([0], [...hrp].map((c) => c.charCodeAt(0) & 31));
}

function convertBits(values, fromBits, toBits, pad) {
  let accumulator = 0;
  let bitCount = 0;
  const output = [];
  const maxValue = (1 << toBits) - 1;
  for (const value of values) {
    if (value < 0 || (value >>> fromBits) !== 0) throw new ValidationError("invalid convertbits value");
    accumulator = ((accumulator << fromBits) | value) >>> 0;
    bitCount += fromBits;
    while (bitCount >= toBits) {
      bitCount -= toBits;
      output.push((accumulator >>> bitCount) & maxValue);
    }
  }
  if (pad && bitCount) output.push((accumulator << (toBits - bitCount)) & maxValue);
  if (!pad && (bitCount >= fromBits || ((accumulator << (toBits - bitCount)) & maxValue))) {
    throw new ValidationError("invalid Bech32 padding");
  }
  return output;
}

function encodeSegwitV0(program, hrp = "bc") {
  if (![20, 32].includes(program.length)) throw new ValidationError("invalid witness v0 length");
  const data = [0, ...convertBits(program, 8, 5, true)];
  const mod = (polymod([...hrpExpand(hrp), ...data, 0, 0, 0, 0, 0, 0]) ^ 1) >>> 0;
  const checksum = Array.from({ length: 6 }, (_, i) => (mod >>> (5 * (5 - i))) & 31);
  return `${hrp}1${[...data, ...checksum].map((v) => BECH32_ALPHABET[v]).join("")}`;
}

function decodeSegwit(address) {
  if (typeof address !== "string" || address.length < 8 || address.length > 90) throw new ValidationError("invalid Bech32 length");
  if (address !== address.toLowerCase() && address !== address.toUpperCase()) throw new ValidationError("mixed-case Bech32");
  const lowered = address.toLowerCase();
  const separator = lowered.lastIndexOf("1");
  if (separator < 1 || separator + 7 > lowered.length) throw new ValidationError("invalid Bech32 separator");
  const hrp = lowered.slice(0, separator);
  const data = [...lowered.slice(separator + 1)].map((char) => {
    const value = BECH32_ALPHABET.indexOf(char);
    if (value < 0) throw new ValidationError("invalid Bech32 character");
    return value;
  });
  if (polymod([...hrpExpand(hrp), ...data]) !== 1) throw new ValidationError("invalid Bech32 checksum");
  const payload = data.slice(0, -6);
  if (payload.length === 0 || payload[0] !== 0) throw new ValidationError("not witness v0");
  const program = Buffer.from(convertBits(payload.slice(1), 5, 8, false));
  if (![20, 32].includes(program.length)) throw new ValidationError("invalid witness v0 program");
  return { hrp, version: 0, program };
}

function entropyToIndices(entropy) {
  if (![16, 20, 24, 28, 32].includes(entropy.length)) throw new ValidationError("invalid BIP39 entropy length");
  const checksumBits = entropy.length * 8 / 32;
  let combined = (bufferToBigInt(entropy) << BigInt(checksumBits));
  combined |= BigInt(sha256(entropy)[0] >>> (8 - checksumBits));
  const count = (entropy.length * 8 + checksumBits) / 11;
  return Array.from({ length: count }, (_, i) => Number((combined >> BigInt(11 * (count - 1 - i))) & 0x7ffn));
}

function reconstructPuzzleMnemonic(repoRoot) {
  const imagePath = pathModule.join(repoRoot, IMAGE_RELATIVE);
  const raw = fs.readFileSync(imagePath);
  const rawDigest = sha256(raw).toString("hex");
  const entropy = sha256(Buffer.from(raw.toString("base64"), "ascii"));
  const indices = entropyToIndices(entropy);
  if (JSON.stringify(indices) !== JSON.stringify(WORD_INDICES)) throw new ValidationError("puzzle word indices differ");
  return { rawDigest, entropy, mnemonic: MNEMONIC, indices };
}

function derive(passphrase, options = {}) {
  const mode = options.mode || "standard";
  const derivationPath = options.path || DEFAULT_PATH;
  const mnemonic = options.mnemonic || MNEMONIC;
  const passBytes = normalizedBytes(passphrase, mode);
  const mnemonicBytes = normalizedBytes(mnemonic, mode);
  const seed = bip39Seed(mnemonic, passphrase, mode);
  const nodes = derivePrivatePath(seed, derivationPath);
  const pubkey = compressedPublicKey(nodes.child.key);
  const program = hash160(pubkey);
  return {
    mode,
    path: derivationPath,
    mnemonicBytes,
    passBytes,
    seed,
    master: nodes.master,
    child: nodes.child,
    pubkey,
    program,
    address: encodeSegwitV0(program),
  };
}

function safeTrace(passphrase, options = {}) {
  const result = derive(passphrase, options);
  return {
    mode: result.mode,
    path: result.path,
    normalized_mnemonic_sha256: sha256(result.mnemonicBytes).toString("hex"),
    normalized_passphrase_sha256: sha256(result.passBytes).toString("hex"),
    seed_sha256: sha256(result.seed).toString("hex"),
    master_fingerprint: hash160(compressedPublicKey(result.master.key)).subarray(0, 4).toString("hex"),
    child_private_sha256: sha256(bigIntTo32(result.child.key)).toString("hex"),
    public_key: result.pubkey.toString("hex"),
    hash160: result.program.toString("hex"),
    address: result.address,
    verdict: result.address === TARGET ? "MATCH" : "NO_MATCH",
  };
}

function assertEqual(actual, expected, label) {
  if (actual !== expected) throw new ValidationError(`self-test failed: ${label}`);
}

function selftest(repoRoot) {
  const phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about";
  assertEqual(
    bip39Seed(phrase, "TREZOR").toString("hex"),
    "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04",
    "BIP39",
  );
  assertEqual(bip39Seed(phrase, "é").toString("hex"), bip39Seed(phrase, "e\u0301").toString("hex"), "NFKD equivalence");

  const master = masterFromSeed(Buffer.from("000102030405060708090a0b0c0d0e0f", "hex"));
  assertEqual(bigIntTo32(master.key).toString("hex"), "e8f32e723decf4051aefac8e2c93c9c5b214313817cdb01a1494b917c8436b35", "BIP32 master key");
  assertEqual(master.chain.toString("hex"), "873dff81c02f525623fd1fe5167eac3a55a049de3d314bb42ee227ffed37d508", "BIP32 master chain");
  const hardened = ckdPrivate(master.key, master.chain, 0x80000000);
  assertEqual(bigIntTo32(hardened.key).toString("hex"), "edb2e14f9ee77d26dd93b4ecede8d16ed408ce149b6cd80b0715a2d911a0afea", "BIP32 hardened key");
  assertEqual(hardened.chain.toString("hex"), "47fdacbd0f1097043b78c63c20c34ef4ed9a111d980047ad16282c7ae6236141", "BIP32 hardened chain");
  const normal = ckdPrivate(hardened.key, hardened.chain, 1);
  assertEqual(bigIntTo32(normal.key).toString("hex"), "3c6cb8d0f6a264c91ea8b5030fadaa8e538b020f0a387421a12de9319dc93368", "BIP32 non-hardened key");
  assertEqual(normal.chain.toString("hex"), "2a7857631386ba23dacac34180dd1983734e444fdbf774041578e9b6adb37c19", "BIP32 non-hardened chain");

  assertEqual(compressedPublicKey(1n).toString("hex"), "0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798", "secp256k1");
  const vectorProgram = Buffer.from("751e76e8199196d454941c45d1b3a323f1433bd6", "hex");
  const vectorAddress = "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4";
  assertEqual(encodeSegwitV0(vectorProgram), vectorAddress, "BIP173 encode");
  assertEqual(decodeSegwit(vectorAddress).program.toString("hex"), vectorProgram.toString("hex"), "BIP173 decode");

  const reconstructed = reconstructPuzzleMnemonic(repoRoot);
  assertEqual(reconstructed.rawDigest, IMAGE_SHA256, "image digest");
  assertEqual(reconstructed.entropy.toString("hex"), ENTROPY_HEX, "image entropy");
  assertEqual(derive("", { mnemonic: reconstructed.mnemonic }).address, SISTER, "empty-passphrase sister");
  const target = decodeSegwit(TARGET);
  assertEqual(`${target.hrp}:${target.version}:${target.program.toString("hex")}`, `bc:0:${TARGET_PROGRAM}`, "target structure");
  return {
    bip39_nfkd: "PASS",
    bip32_hardened_and_normal: "PASS",
    secp256k1: "PASS",
    hash160_p2wpkh_bech32: "PASS",
    puzzle_reconstruction: "PASS",
    target_structure: "PASS",
  };
}

function usage() {
  return "usage: corey_oracle_b.js --selftest | --target-json | [--mode standard|raw-compat] [--path PATH] --inspect CANDIDATE";
}

function main(argv) {
  try {
    if (argv.length === 1 && argv[0] === "--selftest") {
      const repoRoot = pathModule.resolve(__dirname, "..");
      console.log(JSON.stringify(selftest(repoRoot)));
      return 0;
    }
    if (argv.length === 1 && argv[0] === "--target-json") {
      const decoded = decodeSegwit(TARGET);
      console.log(JSON.stringify({ hrp: decoded.hrp, version: decoded.version, program: decoded.program.toString("hex"), checksum: "valid" }));
      return 0;
    }
    let mode = "standard";
    let derivationPath = DEFAULT_PATH;
    let candidate;
    for (let i = 0; i < argv.length; i += 1) {
      if (argv[i] === "--mode" && i + 1 < argv.length) mode = argv[++i];
      else if (argv[i] === "--path" && i + 1 < argv.length) derivationPath = argv[++i];
      else if (argv[i] === "--inspect" && i + 1 < argv.length) candidate = argv[++i];
      else throw new ValidationError(usage());
    }
    if (candidate === undefined) throw new ValidationError(usage());
    console.log(JSON.stringify(safeTrace(candidate, { mode, path: derivationPath })));
    return 0;
  } catch (error) {
    console.error(JSON.stringify({ status: "ERROR", error_type: error.constructor.name }));
    return 2;
  }
}

module.exports = {
  ValidationError,
  bip39Seed,
  ckdPrivate,
  compressedPublicKey,
  decodeSegwit,
  derive,
  derivePrivatePath,
  encodeSegwitV0,
  entropyToIndices,
  hash160,
  masterFromSeed,
  normalizeText,
  parsePath,
  reconstructPuzzleMnemonic,
  safeTrace,
  selftest,
};

if (require.main === module) process.exitCode = main(process.argv.slice(2));
