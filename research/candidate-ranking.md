# Candidate ranking: five puzzles most tractable with software

Checked 2026-08-19. This is a prioritization report, not a new hypothesis ledger. I did not
run a candidate search and did not modify any puzzle folder. I ranked only intentionally
published public treasure hunts whose authors invited solvers to recover the prize.

## Scope and current-state gate

I inspected the root index and every open entry in `1-big-prizes/`, `2-mid-prizes/`, and
`3-small-prizes/`, then read the complete folder record for each finalist: `README.md`,
`puzzle.json`, `analysis/tested.md` and `analysis/leads.md` where present, and the existing
oracle or reference script.

Before ranking, I re-checked the prize addresses. The fresh Bitcoin check changed the result:
VeteranHODL's `bc1qhzy6j4amw26z7e694mgfr7kvzl7xteu54f0a85` now reports 420,000 sats funded and
420,000 sats spent. It is therefore not a current candidate even though the 2026-08-16 index
still labels it funded and open. The five finalists below were observed with these balances:

| Candidate | Fresh observation, 2026-08-19 | Ranking gate |
|---|---|---|
| Crypto Puzzles 2018 #2 | 0.05 ETH at the target address | pass |
| LogicBeach: Powerful Moss | 0.551 ETH at the Base prize contract | pass |
| Arweave Puzzle Weave #12 | 400.00248121 AR | pass |
| Bountiful / Fe | 1 ETH at the registry; each challenge advertises 0.25 ETH | pass |
| Guntis Vitolins | 8.612541554256944620 ETH | pass, but this is an author-controlled wallet |
| VeteranHODL: Hunting Time | 420,000 funded, 420,000 spent | excluded as swept |

The repository's checker could query Bitcoin and Arweave directly. Its configured EVM RPCs
returned HTTP 403 in this environment, so I confirmed the three EVM balances through independent
read-only Blockscout API responses. I ran every finalist's self-test. The pure-Python Arweave
and Fe tests passed. The Crypto Puzzles, LogicBeach, and Guntis tests could not start because
the local environment lacks their declared `ecdsa`, `pycryptodome`, and/or `bip_utils`
dependencies; this is an environment failure, not an oracle failure. Their folder records
contain earlier successful certification results and the exact public witness vectors.

## Ranking

Scores are 1 (poor) to 5 (strong). For `external independence`, 5 means the required puzzle
material is already public and local; 1 means missing outside information is likely fatal.
Prize is deliberately only one factor: a large prize does not rescue an unbounded search.

| Rank | Candidate | Feasibility | Expected compute | Clue quality | Local verification | Prize | External independence | Why it ranks here |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | Crypto Puzzles 2018 #2 | 4.5 | 4.0 | 4.5 | 5.0 | 1.0 | 3.5 | Known glyph alphabet, solved sibling, direct raw-key oracle; the remaining work is mostly deterministic video/image reconstruction. |
| 2 | LogicBeach: Powerful Moss | 4.0 | 4.0 | 4.5 | 5.0 | 3.0 | 4.5 | Carrier, order, wordlist, path, and target wallet are known; the next two image-coordinate tests are cheap and falsifiable. |
| 3 | Arweave Puzzle Weave #12 | 3.5 | 4.0 | 4.0 | 5.0 | 2.5 | 4.0 | Exact 58-character budget, 3 strong sub-answers, and a certified decrypt gate reduce the problem to a named 18-character entity/date string. |
| 4 | Bountiful: Fe compiler bug bounty | 2.5 | 4.0 | 3.0 | 3.0 | 3.5 | 5.0 | All source and bytecode are public; differential testing is bounded. The weakness is that no defect is known to exist in the exercised paths. |
| 5 | Guntis Vitolins: 10 ETH Challenge | 2.5 | 2.0 | 4.0 | 5.0 | 5.0 | 3.0 | Excellent prize and several confirmed anchors, but 16.75 billion witnessed negatives mean the next useful step must improve the word pool before more GPU work. |

## 1. Crypto Puzzles 2018: Puzzle #2

Folder: `3-small-prizes/crypto-puzzles-2018-puzzle-2-0-05eth/`

### Known

- The answer is a raw 64-hex-character secp256k1 private key, not a mnemonic or passphrase.
- The target is `0x1fa8Be9De5bBFE047C72dB8E8E3257128F7661ad`, freshly observed with 0.05 ETH.
- The same author published and paid Puzzle #1. Its revealed 64-hex answer is a complete
  calibration vector for the visual grammar and the key-to-address transform.
- Temporal maximum projection already recovers about 40 to 50 of Puzzle #2's 64 characters.
- The remaining glyphs come from the 16-symbol hexadecimal alphabet, with normal, mirrored,
  and 90-degree-rotated presentations plus a known static decoy.

### Remaining unknown

The exact glyph segmentation, reading order, and roughly 14 to 24 ambiguous hex characters
across the two videos. The number of truly free characters should fall substantially after the
Puzzle #1 grammar and glyph templates are reconstructed.

### Search space and constraints

- Raw current worst case: `16^14` through `16^24`, about `2^56` through `2^96`; not feasible.
- Conditional target after image work: at most 8 unknown hex characters, `N = 16^8 = 2^32 =
  4,294,967,296` candidates.
- Strong reducers: a complete known 16-glyph alphabet from Puzzle #1; fixed 64-character length;
  shared author grammar; temporal alignment; rotations/mirroring limited to a few discrete
  transforms; an exact Ethereum address oracle.

The README calls `16^8` a minutes-scale fallback, but no measured raw-key rate is recorded in
the folder. That runtime should be benchmarked before any loop. At 10 million keys/second,
`t = N / D` is about 7.2 minutes; at 1 million/second it is about 71.6 minutes. More than 8
free nibbles should return the work to image analysis rather than enlarge the sweep.

### Best method

Computer vision first, GPU second. Stabilize and register frames; replay Puzzle #1 end to end;
extract per-symbol templates; classify Puzzle #2 cells under rotation and mirror transforms;
use sequence consistency to resolve pairing and decoy placement. Only then run a bounded GPU
secp256k1/Keccak search over the unresolved nibbles. AI-assisted frame interpretation is useful
for proposing glyph order, but every proposal has an exact local address test.

### Main risk

The videos are referenced rather than stored in the repository. If the available streams have
lost decisive pixels, the visual stage may require a better copy. The author did not state the
Puzzle #2 address directly; the attribution is a strong same-funder/same-amount inference.

## 2. LogicBeach: Powerful Moss

Folder: `2-mid-prizes/logicbeach-powerful-moss-0-54eth/`

### Known

- The POAP clock image, not the audio, is the carrier.
- Twelve clock positions select 12 words from the complete wrapped BIP39 English list; clock
  position supplies the order.
- Three hours are unambiguous. Nine are each close to about three row-derived words.
- The expected derivation is Ethereum BIP44 `m/44'/60'/0'/0/0`, with a small 3-account by
  3-index neighbor sweep.
- The winner address is fixed in the contract, so every checksum-valid phrase is locally and
  exactly verifiable.
- The Base contract was freshly observed with 0.551 ETH.

### Remaining unknown

The precise sampling rule for the nine ambiguous numeral overlays: centroid row, bottom-pixel
row, a wider per-hour row window, or a selector involving the 24 sunburst rays.

### Search space and constraints

- Naive current model: about `3^9 = 19,683` word assignments per ordering, before BIP39
  checksum rejection; four canonical orderings make 78,732 assemblies in the idealized equal-
  width model.
- The actual previous families were larger because candidate counts differ by hour and the
  oracle swept nine derivation paths: more than 3.3 million combinations were tested.
- Opening every hour to a wider row window at once creates an estimated 860-million region and
  was only sampled. The important constraint is to widen one doubtful hour at a time, making
  each run a small multiplier of the already-bounded grid rather than a new Cartesian explosion.
- BIP39 checksum removes roughly 15/16 of mnemonic assemblies before derivation.

The existing measured run processed 1,193,373 assemblies in 131.8 seconds, about 9,055
assemblies/second including checksum and neighbor-path work. A one-hour-at-a-time family of
10 million assemblies would therefore take about 18.4 minutes at the same rate. Exact `N`
must be written from the regenerated per-hour pools before each run.

### Best method

CPU image geometry plus bounded CPU/GPU derivation. Recompute the word-grid row boundaries from
the original 2004x2011 pixels; sample each numeral's bottommost occupied pixel; rank hours by
edge clipping and vertical uncertainty; widen one hour at a time. Only if these fail should ray
length become a new feature. The problem benefits from image analysis and symbolic hypothesis
generation more than from undirected brute force.

### Main risk

The only known image is resolution-limited and no calibration POAP from an earlier solved hunt
exists. Still, the full carrier is public and local, so missing external information is less
likely to be fatal than a wrong interpretation of the sampling rule.

## 3. Arweave Puzzle Weave #12

Folder: `2-mid-prizes/arweave-puzzle-12-400ar/`

### Known

- The answer is exactly 58 case-sensitive characters, formed by concatenating four jigsaw
  sub-answers with no separator.
- The page applies SHA-512 11,513 times and a non-standard CryptoJS 1024-bit-key Rijndael
  decrypt; plaintext containing `"kty":"RSA"` is the exact acceptance gate.
- The pure-Python oracle passed its self-test against solved sibling Puzzle #8.
- Piece 3 is exactly `2111011` (7 characters).
- Piece 1 strongly reads as a 28-character flag/color construction ending in `Blue`.
- Piece 4 contributes 5 characters; its hatching was exhaustively refuted as an ordering rule.
- These length constraints force piece 2 to exactly 18 characters.
- The escrow was freshly observed with 400.00248121 AR and no balance drift.

### Remaining unknown

The exact 18-character reading of the whale-and-`16-03-2020` piece, plus oracle confirmation
that the favored piece-1 reading is correct. `AndreessenHorowitz` has the correct length and a
date-linked investment narrative but already failed across the tested orders and cases.

### Search space and constraints

- Treating piece 2 as arbitrary printable text gives roughly `95^18`, about `4 x 10^35`; that
  is impossible and not a valid plan.
- The meaningful space is a corpus of date-linked company, investor, founder, ticker, whale-
  species, transaction, and round names that normalize to exactly 18 characters, crossed with
  a small set of cases, piece orders, and piece-1 color variants.
- 156,730 assembled 58-character candidates are already negative.
- A prior 104,184-candidate run took 858 seconds, about 121 candidates/second. Thus `N=100,000`
  costs about 13.7 minutes and `N=1,000,000` about 2.3 hours. Any corpus larger than roughly
  870,000 at that rate crosses the repository's two-hour threshold and needs another clue.

### Best method

AI-assisted entity resolution and OSINT corpus construction, then CPU verification. Build a
dated graph around 16 March 2020 and the puzzle author's ecosystem; normalize names under
explicit, logged rules; keep only 18-character strings; cross a small finite set of cases and
orders; feed every full 58-character assembly to the certified oracle. The KDF makes GPU work
less attractive than improving the entity corpus.

### Main risk

The whale may denote a private joke, unpublished co-investor, or non-textual transformation of
the date. That possibility is the main external-information risk; arbitrary character search
cannot compensate for it.

## 4. Bountiful: the Fe compiler bug bounty

Folder: `2-mid-prizes/fe-lang-bountiful-compiler-bounty-1eth/`

### Known

- Seven current Ethereum contracts implement the same 15-puzzle rules using different Fe
  language constructs.
- Every board starts with tiles 14 and 15 swapped. The parity invariant proves no legal move
  sequence can reach the solved board.
- The compiler version is pinned to Fe 26.1.0; about 1,000 lines of source are public.
- Six of eight deployed contracts match verified source on Sourcify. `GameBitboard` and
  `GameTrait` are the two verification gaps.
- The local reference model passed its self-test and can replay moves and calculate parity.
- The registry was freshly observed with 1 ETH. One successful challenge advertises 0.25 ETH;
  the full 1 ETH pot is not the reward for one solve.

### Remaining unknown

A compiler, handwritten-table, packed-bitfield, malformed-calldata, or registry defect that
lets a locked caller make `claim(challenge)` pay despite the parity barrier.

### Search space and constraints

This is not a cryptographic keyspace. The bounded unit is behavioral coverage:

- 7 implementations;
- a small public ABI surface;
- 16 board positions;
- one known start state and one reference transition relation;
- about 1,000 source lines;
- 2 deployed-bytecode verification gaps.

A concrete first campaign can set `N = 7 x 100,000 = 700,000` generated call sequences, with
state comparison after every call and mandatory coverage counters. Runtime depends on the
local EVM harness, so `D` must be measured on a 10,000-sequence pilot before raising `N`. The
important reduction is not random long play: target adjacency constants, array boundaries,
packed 4-bit offsets, enum/trait dispatch, revert paths, and malformed calldata lengths.

### Best method

CPU symbolic review, property-based testing, differential fuzzing, and local-EVM execution.
First recompute every handwritten adjacency and offset constant. Then compile with the pinned
version and compare each call against the reference model after every transition, including
expected reverts. Rebuild and byte-compare the two unverified contracts. Analyze the registry
separately with a local fork. A read-only or local-fork proof is appropriate for research;
nothing in this ranking requires broadcasting a transaction.

### Main risk

There may be no exploitable defect in these code paths. The reference model is not a solution
oracle, and a random campaign can only bound tested behavior, not prove correctness. This ranks
below the image puzzles because their missing answer is known to exist, whereas this hunt asks
the solver to discover an implementation error.

## 5. Guntis Vitolins: 10 ETH Challenge

Folder: `1-big-prizes/guntis-vitolins-metamask-8-6eth/`

### Known

- The target is a 12-word English BIP39 mnemonic, empty passphrase, MetaMask default path
  `m/44'/60'/0'/0/0`.
- Position 1 is `dutch`; position 12 is `parrot`; position 5 is `fog` or `cloud`.
- `fiber` and `fork` are confirmed members with positions not yet fixed.
- Six words come from the video side and six from the blog side, although completed searches
  also tested dropping that partition.
- The archived blog metadata supplied `fork` and `round`, proving metadata is part of the clue
  surface.
- About 16.75 billion derivations across six modern search families are witnessed negatives.
- The target wallet was freshly observed with 8.612541554256944620 ETH.

### Remaining unknown

Seven word values or placements, depending on how the confirmed but unplaced members are
counted, and the complete source word pool. Specifically untested are connecting words,
substring-derived BIP39 words, and metadata fields beyond those already harvested.

### Search space and constraints

- Connecting-word extension: the existing estimate is `N = 1.36 x 10^10` derivations.
- At the recorded `D = 792,000` derivations/second, `t = N/D` is about 17,172 seconds, or
  4.77 hours. This exceeds the two-hour threshold and should be split by a newly justified
  constraint rather than launched as one undifferentiated run.
- Substring extension: `N = 2.78 x 10^11`; at the same rate, `t` is about 351,010 seconds,
  or 97.5 hours. This arithmetic is materially longer than the folder's qualitative
  "about a day" label and should be re-priced before work begins.
- BIP39 checksum rejects roughly 15/16 of last-word assignments; fixed positions 1, 5, and 12,
  the `fiber`/`fork` membership, the 6/6 source budget, and sentence/metadata provenance are
  the main reducers.

### Best method

Metadata and language analysis first; GPU only after the pool changes. Re-read every archived
HTML attribute, tag, image alt field, video tag, description formatting surface, and on-screen
text. Rank newly found BIP39 words by direct provenance. For connecting words, run source-side
and position-conditioned slices with a witness in every partition. Substring search should wait
for a more precise rule from the author's example; otherwise it is a costly expansion with a
weak prior.

### Main risk

The author still controls and has used this wallet, so its balance is not a frozen escrow and
can change independently of a solve. The strong planted-sentence model has already survived a
large amount of negative compute, raising the probability that one required clue sits in an
unrecovered external or metadata surface.

## Recommended execution order

1. Crypto Puzzles #2: reconstruct Puzzle #1's visual grammar and classify Puzzle #2 glyphs.
2. Powerful Moss: bottom-pixel resampling, then one-hour-at-a-time window widening.
3. Arweave #12: build a strictly date-linked 18-character entity corpus and record `N/D/t`.
4. Bountiful: audit constants, then run a measured differential-fuzzing pilot locally.
5. Guntis: complete metadata rereading before authorizing any multi-hour GPU slice.

This order maximizes information gained per hour. It postpones large compute until an upstream
interpretation has reduced the space and keeps every candidate behind an exact local verifier.

## Near misses not selected

- **VeteranHODL: Hunting Time** would otherwise rank near the top because its numeric-index
  hypothesis reduces to a few million candidates, but the fresh chain check shows the entire
  420,000-sat output spent. It must be moved out of the open set before new research.
- **Arweave Puzzle #3** has a certified oracle and local images, but at least two rebus readings
  remain wrong after roughly 330 million candidates; its next useful step is less bounded than
  the five above.
- **Bitcoin Movie Enigma** has a fast verifier but still lacks one film identification, one
  disputed panel, the title-to-word rule, and the 24-of-34 selection field. Too many independent
  semantic gates remain unresolved.
- **GSMG.io** has the largest prize and a certified AES gate, but 335.8 million negatives and
  uncertainty over the correct final target make it less tractable than Guntis despite its
  higher value.
- **Corey Phillips: Kitten Passphrase** is cleanly verifiable but the passphrase is an
  unconstrained author-chosen secret after about 1.16 billion negatives; missing external
  information is more likely than a remaining bounded software search.
