# Model decisions and provenance

Date: 4 November 2026. Decision status: researched specification, awaiting implementation acceptance.

No model weights were downloaded or executed during this research. File lengths and SHA-256 values below are upstream artifact metadata, not independently recomputed checksums. There are no Commonstar device, latency, memory, teaching-quality or learning-outcome measurements yet.

## 1. Selected profiles

Commonstar requires capable on-device generation and local retrieval. A workstation is an optional additional worker; it never owns the authoritative learner vault. Model choice can change without changing record ownership or the export format.

| Role | Selected model | Parameter accounting | Intended first use |
| --- | --- | --- | --- |
| Standard learner | Gemma 4 E4B Instruct, official Google QAT Q4_0 GGUF | 4.5B effective; 8B including per-layer embeddings | Full local tutoring, organization and bounded proposals |
| Compact learner | Ministral 3 3B Instruct 2512, official Mistral Q4_K_M GGUF | 3.4B language model; separate 0.4B vision encoder | Complete smaller local installation |
| Ubuntu workstation | Gemma 4 31B Instruct, official Google QAT Q4_0 GGUF | 30.7B in Google's architecture table | Optional larger locally hosted computation |
| Workstation comparison | Gemma 4 26B A4B Instruct, official Google QAT Q4_0 GGUF | 25.2B total; 3.8B active | Compare measured latency, quality and memory with 31B |
| Learner comparison | Ministral 3 8B Instruct 2512, official Mistral Q4_K_M GGUF | 8.4B language model; separate 0.4B vision encoder | Compare at approximately the E4B artifact footprint |
| Local embeddings | Google EmbeddingGemma 2, text-only BF16 GGUF converted by llama.cpp maintainers | 270M text backbone; 740M with optional vision/audio encoders | Bilingual semantic retrieval; full 768-dimensional vectors |

Parameter facts come from the [Gemma 4 model card](https://ai.google.dev/gemma/docs/core/model_card_4), [Ministral 3B card](https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512), [Ministral 8B card](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512) and [EmbeddingGemma 2 card](https://huggingface.co/google/embeddinggemma-2).

These are engineering selections, not measured winners for children's education. A model's size, general benchmark score or publisher's safety evaluation does not establish age appropriateness, subject correctness, or improved learning. Workstation Gemma is not claimed equivalent to an unspecified proprietary frontier model. English and Spanish tutoring and retrieval need explicit Commonstar evaluations.

“Effective” and “active” counts describe architecture; they do not determine the bytes stored or the memory needed. QAT Q4_0 and Q4_K_M are distinct packaged quantizations. Test each selected artifact instead of treating every four-bit conversion as equivalent.

## 2. Modality boundaries

| Selected model | Native inputs described by upstream | Output | Commonstar initial activation |
| --- | --- | --- | --- |
| Gemma 4 E4B | Text, image, audio | Text | Text; image/audio after separate integration acceptance |
| Gemma 4 31B | Text, image; no native audio encoder | Text | Text; image after separate acceptance |
| Gemma 4 26B A4B | Text, image; no native audio encoder | Text | Text comparison profile |
| Ministral 3 3B / 8B | Text, image | Text | Text; vision projector is optional |
| EmbeddingGemma 2 | Text; optional vision and audio encoders | Vectors | Text only |

The [Gemma 4 architecture table](https://ai.google.dev/gemma/docs/core/model_card_4) distinguishes the audio-capable E4B from 31B and 26B. Audio understanding does not provide speech generation. Spoken output requires a separately selected and licensed local speech engine/voice. Audio input to 31B, 26B or Ministral requires a separately validated transcription path. An installed projector does not by itself prove the shipped HTTP/IPC route supports that modality.

## 3. Immutable artifact identities

The machine-readable equivalent belongs in `models/catalog.json`. Each revision identifies the publisher's repository state, and each SHA-256 identifies the named binary according to its upstream large-file pointer. Preserve the original license and provenance when redistributing. Model artifacts do not belong in ordinary Git source history.

### Standard learner

- Repository: [google/gemma-4-E4B-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf/tree/4b4a2c1d584be7264f87aac328a1bc739ce81b6c)
- Revision: `4b4a2c1d584be7264f87aac328a1bc739ce81b6c`
- File: `gemma-4-E4B_q4_0-it.gguf`
- Representation: QAT Q4_0; license: Apache-2.0
- Bytes: 5,154,941,280
- Upstream SHA-256: `676c35070db6dbe52f93e9c864ee0fba4eddea94b9c875d9cb10daff453fbaee`
- Optional projector at the same package revision: `gemma-4-E4B-it-mmproj.gguf`; 991,552,256 bytes; SHA-256 `7498a37cb619e55f2fcf87eb931f56e99389ed6d432e4c5c66110694c0d65578`

### Ubuntu workstation

- Repository: [google/gemma-4-31B-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-4-31B-it-qat-q4_0-gguf/tree/59dde24573e7e61570dba08b18a2e1fe246955ed)
- Revision: `59dde24573e7e61570dba08b18a2e1fe246955ed`
- File: `gemma-4-31B_q4_0-it.gguf`
- Representation: QAT Q4_0; license: Apache-2.0
- Bytes: 17,651,001,568
- Upstream SHA-256: `179cfb99212709597eae5929112cfca677e1bbf566178b479ae1da0c4772874b`

### Workstation comparison

- Repository: [google/gemma-4-26B-A4B-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-4-26B-A4B-it-qat-q4_0-gguf/tree/d1c082be9cf3c8a514acf63b8761f4b41935842e)
- Revision: `d1c082be9cf3c8a514acf63b8761f4b41935842e`
- File: `gemma-4-26B_q4_0-it.gguf`
- Representation: QAT Q4_0; license: Apache-2.0
- Bytes: 14,439,363,584
- Upstream SHA-256: `3eca3b8f6d7baf218a7dd6bba5fb59a56ee25fe2d567b6f5f589b4f697eca51d`

### Compact learner

- Repository: [mistralai/Ministral-3-3B-Instruct-2512-GGUF](https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512-GGUF/tree/eb599d408350ea2bb60452cb86be7c7b2fc28227)
- Revision: `eb599d408350ea2bb60452cb86be7c7b2fc28227`
- File: `Ministral-3-3B-Instruct-2512-Q4_K_M.gguf`
- Representation: Q4_K_M; license: Apache-2.0
- Bytes: 2,147,023,008
- Upstream SHA-256: `9ed150d4367e68df0ac8e1540f6ddc65b42d0ee26378329d1ecbca60f93fc5f8`
- Optional projector at the same package revision: `Ministral-3-3B-Instruct-2512-BF16-mmproj.gguf`; 841,501,856 bytes; SHA-256 `70ca26e41ecea9da997e2887462ad68b848fbf64da011ff4107bbe7353519ee0`

### Learner comparison

- Repository: [mistralai/Ministral-3-8B-Instruct-2512-GGUF](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512-GGUF/tree/0102285ad796bd99af90f58de616092e5630e970)
- Revision: `0102285ad796bd99af90f58de616092e5630e970`
- File: `Ministral-3-8B-Instruct-2512-Q4_K_M.gguf`
- Representation: Q4_K_M; license: Apache-2.0
- Bytes: 5,198,911,904
- Upstream SHA-256: `33e7a72cf5e6e2cfc2f2847075acc013d68bba023e35310cef86b5cf8fdca761`

### Default embedding

- Repository: [ggml-org/embeddinggemma-2-GGUF](https://huggingface.co/ggml-org/embeddinggemma-2-GGUF/tree/6ea3e3a309d12a4779cfda98b8c19800d2d5da71)
- Revision: `6ea3e3a309d12a4779cfda98b8c19800d2d5da71`
- File: `embeddinggemma-2-BF16.gguf`
- Representation: BF16; license: Apache-2.0
- Bytes: 557,950,176
- Upstream SHA-256: `68bae29d62fb8c7d23e98d21fd4662753ddd636e6b62b8a70dfe059a9844f216`
- Original checkpoint: [google/embeddinggemma-2](https://huggingface.co/google/embeddinggemma-2), revision `f9972ac22e696a105c482202646979e33e4b5a1e`
- Optional projector at the same package revision: `mmproj-embeddinggemma-2-BF16.gguf`; 982,074,816 bytes; SHA-256 `cc8d7eb30a9984c5128d6b1ccdec7510bfce213dc92a840be0d20e2a62b26bcd`

### Compact embedding candidate

- Repository: [ggml-org/embeddinggemma-2-GGUF](https://huggingface.co/ggml-org/embeddinggemma-2-GGUF/tree/6ea3e3a309d12a4779cfda98b8c19800d2d5da71)
- Revision: `6ea3e3a309d12a4779cfda98b8c19800d2d5da71`
- File: `embeddinggemma-2-Q8_0.gguf`
- Representation: Q8_0; license: Apache-2.0
- Bytes: 309,855,456
- Upstream SHA-256: `2188ac1deca4b77dffefd603c2776a9d76d9d74ec01841392982ebb840b09135`
- Original checkpoint: [google/embeddinggemma-2](https://huggingface.co/google/embeddinggemma-2), revision `f9972ac22e696a105c482202646979e33e4b5a1e`
- Optional projector at the same package revision: `mmproj-embeddinggemma-2-Q8_0.gguf`; 554,821,056 bytes; SHA-256 `0531309472a6bc6f4b146c3736eee7795ec9db1903c25490d3c937490cef6dd8`

The Google QAT and Mistral GGUF repositories above are model-publisher packages. `ggml-org/embeddinggemma-2-GGUF` is a runtime-maintainer conversion, not a Google-published GGUF. Its [conversion commit](https://huggingface.co/ggml-org/embeddinggemma-2-GGUF/commit/6ea3e3a309d12a4779cfda98b8c19800d2d5da71) records the upstream checkpoint revision. The 31B, 26B and comparison 8B entries do not pin optional projector artifacts here; a release that enables those modalities must add verified identities before activation.

## 4. Embedding contract

EmbeddingGemma 2 was released on 6 October 2026 according to [Google's release notes](https://ai.google.dev/gemma/docs/releases). The [official card](https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2) describes 100-plus languages, an 8,192-token input limit and 768-dimensional native vectors. Optional vision and audio encoders account for 170M and 300M parameters respectively. The default text package does not need either encoder.

Use these retrieval templates, with `none` as an absent document title:

```text
Query:    task: search result | query: {query}
Document: title: {title} | text: {content}
```

Use 768 dimensions initially and L2-normalize valid vectors. Store the model revision, representation, dimensions, template, chunking and normalization policy with the index version. Reject mixed-version comparison; regenerate derived vectors from authoritative local records after an incompatible change. Keep profile/permission filters ahead of any candidates entering model context.

**BF16 or F32 execution is required.** The [official numerical-precision guidance](https://huggingface.co/google/embeddinggemma-2) warns against FP16, which can yield invalid or degraded embeddings. Q8_0 weight compression does not make an FP16 activation path safe. The Q8_0 file is a candidate for evaluation; BF16 remains the initial accuracy baseline.

Native architecture support was merged through [llama.cpp PR #30054](https://github.com/ggml-org/llama.cpp/pull/30054), commit [`4fbc76dec51d0add466f0210855c0596589b60d4`](https://github.com/ggml-org/llama.cpp/commit/4fbc76dec51d0add466f0210855c0596589b60d4). Use a tested runtime containing that support and subsequent relevant fixes. Native GGUF loading does not require `trust_remote_code=True` or execution of model-repository Python. The source pin in `distro/runtime-lock.json` is a researched baseline until compiled and exercised.

Startup checks must verify finite values, 768 dimensions, nonzero norms, repeatability within declared numeric tolerance and expected retrieval rankings on a fixed fixture. Evaluate English, Spanish and cross-language retrieval, equations, negation, corrected facts and similar distractors. Keep local FTS5/structured retrieval usable when semantic indexing fails, and display the reduced capability honestly.

[Nomic Embed Text v2 MoE](https://huggingface.co/nomic-ai/nomic-embed-text-v2-moe) is an Apache-2.0 multilingual alternative: 475M total/305M active parameters, with a 512-token input limit. Its official Python quickstart enables remote code; separately audited native packaging can avoid that. [Nomic v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) is Apache-2.0 and English-focused. The default choice reflects provenance, bilingual scope, context flexibility and runtime availability, not an unmeasured quality victory.

## 5. Runtime and resource acceptance

llama.cpp is the selected inference engine, but architecture support in upstream source is distinct from a working Commonstar installation. Bind the package, tokenizer/chat template, runtime commit, compiled backend, flags and output contract together. Validate the actual executable's help instead of copying commands from a different release: upstream CLI names and defaults have changed. See the [runtime project](https://github.com/ggml-org/llama.cpp) and the immutable source reference in `distro/runtime-lock.json`.

Initial application context budgets are 8,192 tokens on the learner and 16,384 on the workstation; a 32,768-token host profile requires evaluation. These are project budgets, not model ceilings or measurements. Plan tests around 16 GB full-client RAM, 8 GB compact-client RAM and 32–64 GB workstation RAM, without representing these as measured minimums or forcing hardware purchases.

Weight bytes exclude operating-system overhead, UI, indexes, projectors, KV caches, scratch buffers and concurrency. CPU-only execution and slow jobs remain supported design paths. Measure load time, peak resident memory, time to first token, generation rate, thermal behavior and cancellation on actual equipment. Keep reading, saving and cancelling responsive while an inference worker is busy. Hardware scarcity cannot silently authorize remote inference.

Generation and embedding workers receive bounded inputs and read-only model files. They do not receive vault keys, unrestricted filesystem access or executable tool authority. Trusted code validates model proposals and owns all durable commits.

## 6. Licensing, naming and deployment claims

The selected packages are Apache-2.0 according to their publisher/model cards. Retain license texts, copyright notices and applicable notices when distributing model packs; do not relabel upstream weights under Commonstar's application license. Describe the product as **open source software with open model weights**. Those licenses do not establish that training data or the complete training process are published or reproducible.

Commonstar Learning OS is the project's proposed identity. No model choice, repository publication or preliminary exact-name search supplies trademark clearance, official Texas affiliation, district authorization or educational endorsement. No child-safety certification or learning gain has been established by this research.

The [Texas DIR list](https://dir.texas.gov/information-security/covered-applications-and-prohibited-technologies) creates an institutional-review concern for Alibaba/Qwen and BAAI defaults. Selecting other packages avoids that default dependency; it does not establish legal compliance for every deployment. Applicability depends on the institution, device and policy. The project makes no claim that all local Qwen use in every Texas school district is unlawful, or that an election automatically changes existing restrictions.

Release promotion requires verified downloads, license/notices review, actual runtime loading, correct capability declarations, local privacy checks, task evaluation and separately documented device and educational evidence. Source review and a populated manifest establish none of those outcomes by themselves.
