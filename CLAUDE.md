# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

AI/ML 논문 PDF 또는 URL을 입력받아 연구자 수준의 섹션별 요약을 HTML로 생성하는 워크플로우.
수식은 KaTeX로 렌더링, 그림/테이블은 상세 설명, 비판적 분석 포함.

## 프로젝트 구조

- `CLAUDE.md` — 워크플로우 지침 및 템플릿
- `index.html` — 요약 목록 및 네비게이션 (자동 생성/업데이트)
- `*.html` — 개별 논문 요약 파일 (`{YYYYMMDD}_{첫저자성}_{키워드}.html` 형식)

빌드 시스템, 테스트, 린트 등의 도구는 없음. 정적 HTML 파일만 생성하는 프로젝트.

## 자동 실행 규칙

- `pdf_directory/`에 새 PDF가 있으면, 사용자 확인 없이 즉시 요약 워크플로우(Phase 1~3 + index.html 업데이트 + 브라우저 열기 + git commit & push)를 실행한다
- 새 PDF 판별: 기존 요약 HTML 파일명과 대조하여, 아직 요약이 생성되지 않은 PDF를 새 논문으로 간주한다
- 여러 개의 새 PDF가 있으면 순차적으로 모두 처리한다

### URL 입력 처리
- 사용자가 논문 URL(arXiv, 기타)만 제공하면, PDF를 `pdf_directory/`에 자동 다운로드한 뒤 요약 워크플로우를 실행한다
- arXiv URL 변환: `abs` → `pdf` (예: `https://arxiv.org/abs/2602.10090` → `https://arxiv.org/pdf/2602.10090`)
- 다운로드 명령: `curl -L -o pdf_directory/{arxiv_id}.pdf {pdf_url}`
- 여러 URL이 제공되면 모두 다운로드 후 순차적으로 요약한다

### 파일 목록 입력 처리
- 사용자가 `.txt` 또는 `.csv` 파일 경로를 제공하면, 파일을 읽어 URL/파일경로 목록을 추출한 뒤 순차적으로 처리한다
- `.txt`: 한 줄에 하나의 URL 또는 파일 경로. 빈 줄과 `#`으로 시작하는 주석은 무시
- `.csv`: `url`, `path`, `link` 등의 컬럼명에서 URL/경로를 추출. 컬럼명이 없으면 첫 번째 컬럼 사용
- URL은 PDF 다운로드 후 요약, 로컬 파일 경로는 `pdf_directory/`에 복사 후 요약

---

## 워크플로우 (3단계)

### Phase 1 — 빠른 개요 (Quick Overview)
1. 메타데이터 추출: 제목, 저자, 학회/저널, 연도
2. 논문 구조(섹션 목록) 파악
3. TL;DR 생성 (문제 → 해결 → 왜 작동하는가 → 직관적 비유)
4. 핵심 기여(Key Contributions) 3~5개 bullet 정리

### Phase 2 — 섹션별 정밀 요약 (Deep Dive)
- 각 섹션을 순서대로 깊이 있게 순차 처리

### Phase 3 — 검증 (Verification)
요약 파일 작성 완료 후, Task agent(subagent_type: general-purpose)를 실행하여 원문 대비 요약을 검증한다.

검증 에이전트에게 전달할 것:
- 원문 PDF/URL 경로
- 생성된 요약 파일 경로

**검증 항목 체크리스트:**

| # | 항목 | 확인 내용 |
|---|------|----------|
| 1 | 섹션 완전성 | 원문의 모든 섹션이 요약에 포함되었는가? 누락된 섹션 목록 제시 |
| 2 | 수치 정확성 | 정확도, F1, 파라미터 수 등 핵심 수치가 원문과 일치하는가? 불일치 항목 구체적으로 나열 |
| 3 | 수식 검증 | 주요 수식이 원문과 동일한가? (기호, 첨자, 수식 번호) 오류 있으면 올바른 수식 제시 |
| 4 | 누락된 핵심 내용 | 중요한 실험 결과, ablation, 주요 주장이 빠지지 않았는가? |
| 5 | 환각 검출 | 원문에 없는 내용이 요약에 추가되지 않았는가? (비판적 분석 섹션 제외) |
| 6 | 템플릿 준수 | 메타데이터, TL;DR, 핵심 기여, 비판적 분석 등 모든 필수 섹션이 채워졌는가? |
| 7 | 용어 일관성 | 약어가 첫 등장 시 풀어쓰기 되었는가? 기술 용어가 영문으로 유지되었는가? |

**검증 에이전트 출력 형식:**
```
## 검증 결과

### 통과 항목
- [x] 항목명: 간단한 확인 메시지

### 수정 필요 항목
- [ ] 항목명: 구체적인 문제 설명과 수정 제안
  - 원문: "..."
  - 요약: "..."
  - 제안: "..."

### 종합 판정
- PASS: 수정 사항 없음 → 완료
- MINOR: 경미한 수정 필요 → 자동 수정 후 완료
- MAJOR: 중대한 누락/오류 → 해당 섹션 재작성 필요
```

**검증 후 처리:**
- **PASS**: 사용자에게 완료 보고
- **MINOR**: 지적된 항목을 자동으로 수정한 뒤 완료 보고
- **MAJOR**: 지적된 섹션을 원문과 대조하여 재작성. 재작성 후 해당 항목만 재검증

---

## AI 논문 특화 가이드라인

### 반드시 포착해야 할 핵심 요소
- **모델 아키텍처**: 구조를 층(layer) 단위로 설명. 입력→출력 흐름을 명확히
- **손실 함수 (Loss Function)**: 전체 목적함수와 각 항(term)의 역할. 하이퍼파라미터 포함
- **학습 세부사항**: optimizer, learning rate (schedule 포함), batch size, epoch, hardware
- **데이터셋**: 이름, 규모, 전처리 방법, train/val/test 분할
- **베이스라인 비교**: 어떤 모델과 비교했는지, 공정한 비교인지
- **Ablation Study**: 어떤 컴포넌트를 제거/변경했을 때 성능 변화
- **SOTA 달성 여부**: 어떤 벤치마크에서, 얼마나 개선했는지

### AI 분야별 주의사항

| 분야 | 중점 확인 사항 |
|------|---------------|
| NLP / LLM | tokenizer, context length, pre-training corpus, fine-tuning 전략, 평가 벤치마크 (MMLU, HumanEval 등) |
| Computer Vision | backbone, resolution, augmentation, FLOPs/파라미터 수 |
| Reinforcement Learning | environment, reward design, exploration 전략, sample efficiency |
| Generative Model | 생성 품질 지표 (FID, IS, CLIP score), sampling 방법, inference 속도 |
| Graph Neural Network | 그래프 구성 방법, message passing 방식, scalability |
| Multimodal | modality 간 alignment 방법, fusion 전략, 각 modality의 encoder |

### 비판적 분석 시 AI 논문 체크리스트
- 실험이 충분한 seed/run으로 반복되었는가? (표준편차 보고 여부)
- 공정한 베이스라인 비교인가? (같은 파라미터 수, 같은 데이터)
- Ablation이 핵심 주장을 뒷받침하는가?
- 계산 비용(compute cost) 대비 성능 개선이 실용적인가?
- 코드/데이터 공개 여부

---

## 출력 형식

### 항상 HTML (.html)
모든 요약은 **HTML로 출력**한다. 브라우저에서 수식 렌더링, 하이라이트, 테이블 스타일링이 즉시 동작하며, index.html을 통해 요약 간 네비게이션이 가능하다.

**수식 라이브러리**: KaTeX를 사용한다 (MathJax보다 렌더링이 빠름). 기존 MathJax 코드가 있는 HTML과 합칠 때는 MathJax를 제거하고 KaTeX로 통일할 것.

**하이라이트 기능**: 본문에서 `##텍스트##`로 감싼 부분은 노란색 하이라이트로 렌더링한다. 이를 위한 JS를 KaTeX 로드 이후에 배치.

HTML 파일 상단에 아래 템플릿을 사용:
```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{논문 제목}</title>
<!-- KaTeX (수식 렌더링) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {delimiters: [
    {left: '$$', right: '$$', display: true},
    {left: '$', right: '$', display: false}
  ]});"></script>
<!-- ##...## 하이라이트 -->
<script>
document.addEventListener("DOMContentLoaded", function() {
  const el = document.getElementById('main-content');
  if (el) {
    el.innerHTML = el.innerHTML.replace(/##([\s\S]*?)##/g,
      '<span style="background-color:#ffeb3b;color:#000">$1</span>');
  }
});
</script>
<style>
  body { max-width: 860px; margin: 2rem auto; padding: 0 1rem; font-family: 'Noto Sans KR', sans-serif; line-height: 1.8; color: #1a1a1a; }
  h1 { border-bottom: 2px solid #333; padding-bottom: 0.3rem; }
  h2 { border-bottom: 1px solid #ccc; padding-bottom: 0.2rem; margin-top: 2rem; }
  h3 { margin-top: 1.5rem; }
  table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
  th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
  th { background: #f5f5f5; }
  blockquote { border-left: 4px solid #4a90d9; padding: 0.5rem 1rem; margin: 1rem 0; background: #f8f9fa; }
  code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
  .metadata { background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
  .critical-analysis { background: #fff8f0; padding: 1rem; border-radius: 8px; border-left: 4px solid #e67e22; }
  .takeaways { background: #f0f8f0; padding: 1rem; border-radius: 8px; border-left: 4px solid #27ae60; margin: 1rem 0; }
  .flow-diagram { background: #f5f5f5; padding: 1rem; border-radius: 8px; font-family: monospace; white-space: pre; line-height: 1.5; margin: 1rem 0; overflow-x: auto; }
  .tldr { background: #f0f4ff; padding: 1rem; border-radius: 8px; border-left: 4px solid #3498db; margin: 1rem 0; }
  .qa-block { background: #e8f4fd; padding: 0.8rem 1rem; border-radius: 6px; margin: 0.8rem 0; border-left: 3px solid #2196F3; }
  .personal-notes { background: #f0f7f0; padding: 1rem; border-radius: 8px; border-left: 4px solid #4caf50; margin-top: 2rem; }
</style>
</head>
<body>
<div id="main-content">
<!-- 본문 내용 -->
</div>
</body>
</html>
```

### HTML 구조 규칙 (일관성 필수)

모든 요약 HTML은 아래 구조 규칙을 반드시 따른다. 파일 간 스타일 불일치를 방지하기 위함이다.

**메타데이터** — `<div class="metadata">` 내부에 `<ul><li>` 형식 사용:
```html
<div class="metadata">
<ul>
  <li><strong>저자</strong>: ...</li>
  <li><strong>소속</strong>: ...</li>
  <li><strong>학회/저널</strong>: ...</li>
  <li><strong>연도</strong>: ...</li>
  <li><strong>링크</strong>: <a href="...">...</a></li>
</ul>
</div>
```

**TL;DR** — `<div class="tldr">` 래퍼 + `<ul><li>` 형식. 항목: 문제, 해결, 왜 작동하는가, 비유:
```html
<h2>TL;DR</h2>
<div class="tldr">
<ul>
  <li><strong>문제</strong>: ...</li>
  <li><strong>해결</strong>: ...</li>
  <li><strong>왜 작동하는가</strong>: ...</li>
  <li><strong>비유</strong>: ...</li>
</ul>
</div>
```

**핵심 기여** — `<ol>` (ordered list) 사용. 콜론(`:`) 뒤 설명:
```html
<h2>핵심 기여 (Key Contributions)</h2>
<ol>
  <li><strong>기여 제목</strong>: 설명...</li>
</ol>
```

**알고리즘 흐름도** — `<pre>` 대신 `<div class="flow-diagram">` 사용:
```html
<div class="flow-diagram">입력(q) → [Stage 1] ...
       → [Stage 2] ...</div>
```

**`<strong>` 뒤 구분자** — `<strong>제목</strong>:` 형식 사용 (콜론 뒤 공백). `<strong>제목:</strong>`가 아님에 주의.

### index.html 자동 업데이트
새 요약 HTML을 생성할 때마다 프로젝트 루트의 `index.html`을 업데이트한다:
1. 새 요약을 `<ul id="paper-list">` 안에 아래 형식의 `<li>` 항목으로 추가:
```html
<li class="paper-item"
    data-tags="태그1,태그2,태그3"
    data-date="YYYY-MM-DD"
    data-authors="저자 et al."
    data-venue="학회/저널">
  <div class="paper-top">
    <div class="paper-title"><a href="파일명.html">논문 제목</a></div>
    <div class="paper-date">YYYY-MM-DD</div>
  </div>
  <div class="paper-meta">저자 · 소속 · 연도</div>
  <div class="paper-tags">
    <span class="tag">태그1</span>
    <span class="tag">태그2</span>
  </div>
</li>
```
2. 최신 항목이 위에 오도록 역시간순 정렬 유지
3. `data-tags`에 분야 태그를 쉼표로 구분하여 넣으면, 태그 필터 패널에 자동 반영됨 (JS가 동적으로 수집). `data-tags`와 `<span class="tag">` 내용을 일치시킬 것
4. 총 편수, 태그 카운트 등 모든 통계는 JS가 자동 계산하므로 수동 업데이트 불필요
5. index.html이 없으면 새로 생성

---

## 입력 처리 가이드라인

- **PDF 파일**: Read 도구로 직접 읽기 (Claude Code가 PDF 지원). 페이지가 많은 PDF는 `pages` 파라미터로 나눠 읽기 (최대 20페이지씩).
- **URL (arXiv 등)**: WebFetch로 내용 가져오기. arXiv는 PDF URL 변환 (`abs` → `pdf`).

### 웹 검색을 활용한 배경 지식 보강
논문 요약 시 내용이 어렵거나 구체적인 설명이 필요한 경우, **WebSearch/WebFetch를 적극 활용**하여 관련 정보를 보강한다:
- 논문이 기반으로 하는 선행 연구의 핵심 개념이 PDF만으로 충분히 이해되지 않을 때
- 분야 특화 용어나 방법론에 대한 추가 설명이 필요할 때
- 비교 대상 베이스라인/벤치마크의 맥락을 독자에게 전달하기 위해
- 인용된 핵심 참고문헌의 내용을 간략히 요약하여 배경 설명을 풍부하게 할 때

---

## 수식 / 그림 / 테이블 처리 규칙

| 요소 | 규칙 |
|------|------|
| 수식 | 인라인 `$...$`, 블록 `$$...$$`. 원문 notation 유지. 수식 번호 `(1)` 등 원문과 일치 |
| 수식 유도 | 핵심 유도 과정은 step-by-step으로 재현. 중간 생략 시 어떤 성질을 사용했는지 명시 |
| 그림 | `> **[Figure N 설명]**: 그림의 내용과 의미를 상세히 기술` |
| 테이블 | Markdown 테이블로 재현. 큰 테이블은 핵심 행만 발췌 + 전체 트렌드 설명 |
| 알고리즘 | 코드블록으로 pseudo-code 재현 |
| 아키텍처 다이어그램 | 텍스트로 입력→처리→출력 흐름을 단계별로 기술 |
| 하이라이트 | `##텍스트##`로 감싸면 HTML에서 노란 배경으로 강조 표시 |

### 하이라이트 (`##...##`) 적용 기준

HTML 출력 시 아래에 해당하는 부분을 `##...##`로 감싸서 강조한다:

- **논문의 핵심 기여/novelty**: 이 논문만의 독창적 아이디어나 메커니즘
- **SOTA 수치**: 벤치마크 최고 성능 달성 결과
- **핵심 인사이트**: 실험에서 발견된 가장 중요한 관찰 (예: entropy collapse 지연)
- **실용적 trade-off**: 비용 대비 성능 등 실무에 유용한 정보
- **놀라운 결과**: 기대와 다르거나 주목할 만한 발견
- **범용성/한계**: 다른 방법에도 적용 가능하다거나, 학습 시에만 적용된다는 등 중요한 scope 정보

**주의**: 남용하지 않는다. 한 섹션에 1~2개 정도가 적절. 전체 요약에서 8~12개 이내.

---

## 언어 규칙

- 기본 언어: **한국어**
- 기술 용어: 영어 원문 유지 (예: "attention mechanism", "gradient descent")
- 형식: `한국어 설명 (English term)`

---

## 서술 품질 가이드라인

### 스토리라인 우선
단순 섹션 나열이 아니라 **"왜 → 어떻게 → 효과"** 흐름을 만든다:
- **문제 (Problem)**: 기존 방법의 한계가 무엇인가?
- **핵심 아이디어 (Idea)**: 이 논문의 해결 방식을 한 문장으로
- **작동 원리 (How)**: 구체적 메커니즘
- **검증 (Evidence)**: 실험이 주장을 뒷받침하는가?

### Background는 충분히 설명
선행 연구/배경 지식은 **독자가 본 논문의 기여를 온전히 이해할 수 있도록 충분히** 서술한다:
- 본 논문이 기반으로 하는 기존 방법의 핵심 개념과 수식을 설명한다
- 기존 방법의 한계점을 구체적으로 짚어, 본 논문의 motivation이 자연스럽게 연결되도록 한다
- 해당 분야에 익숙하지 않은 연구자도 이해할 수 있는 수준의 배경 설명을 목표로 한다
- 단, 본 논문과 직접 관련 없는 지엽적인 세부사항은 생략한다

### 용어는 논문 맥락에서 충분히 설명
기술 용어가 일반적인 의미만으로는 이해하기 어려운 경우, **해당 논문에서 그 용어가 구체적으로 무엇을 지칭하는지** 설명한다:
- 논문 고유의 용어(예: 저자가 새로 정의한 개념)는 정의와 함께 왜 그렇게 부르는지 설명
- 분야 공통 용어라도 논문에서 특수한 의미로 사용되면 그 차이를 명시
- 약어뿐 아니라 개념 자체가 낯설 수 있는 용어는 첫 등장 시 1~2문장으로 맥락 설명 추가
- 예: "draft"가 단순한 초안이 아니라 "모델이 생성한 후보 응답"을 의미하는 경우, 그 맥락을 밝힌다

### 수식에는 반드시 직관을 병행
수식만 나열하지 않는다. 모든 핵심 수식 뒤에 **"직관적으로 말하면..."** 한 줄 설명을 추가한다.
- 나쁜 예: 수식만 나열
- 좋은 예: 수식 + "즉, 모델이 자기 자신의 최선 답안을 참고하여 더 나은 답을 내도록 학습한다"

### 실험은 "왜 → 결과 → 뒷받침" 구조로 서술
각 실험/ablation을 설명할 때 반드시 3가지를 명확히 한다:

1. **실험 의도 (왜 이 실험을 했는가)**: 이 실험이 답하려는 질문이 무엇인지 먼저 제시
   - 예: "iGRPO의 성능 향상이 GRPO에만 특화된 것인지, 다른 방법에도 범용적인지 확인하기 위해..."
2. **결과**: 테이블/수치 제시
3. **이 실험이 뒷받침하는 주장**: 결과가 논문의 어떤 claim을 지지하는지 명시적으로 연결
   - 예: "DAPO와 GSPO 모두에서 유사한 개선이 관찰되므로, gain의 출처는 GRPO 특유의 디테일이 아니라 refinement interface 자체이다."

전체 실험 섹션 시작 시, 논문이 답하려는 핵심 질문 목록을 먼저 나열하고, 각 실험이 어떤 질문에 대응하는지 매핑하면 좋다.

### 실험 결과에 패턴 분석 추가
테이블 나열 후 반드시 **패턴/인사이트**를 서술한다:
- 어떤 조건에서 효과가 가장 큰가? (모델 크기, 난이도, base 모델 강도 등)
- 효과가 작거나 없는 경우는? 그 이유는?

### 알고리즘 흐름도 포함
논문에 Algorithm이 있으면 **텍스트 기반 흐름도**로 재현한다:
```
입력(q) → [Stage 1] N개 draft 생성 → best draft 선택
       → [Stage 2] q + best draft → G개 refinement → GRPO 업데이트
```

### Key Takeaways 섹션 필수
비판적 분석 뒤에 **"이 논문에서 가져갈 것"**을 3~5개 bullet으로 정리한다. 연구자가 이 논문을 읽어야 할 이유와 실무 적용 가능성에 집중.

---

## 정확성 기준

- 원문에 없는 내용 추가 금지 (비판적 분석, Key Takeaways 섹션 제외)
- 수식 번호는 원문과 일치시킬 것
- 약어는 첫 등장 시 풀어쓰기 (예: GAN (Generative Adversarial Network))
- 섹션 누락 없이 전체 커버
- 하이퍼파라미터, 데이터셋 규모 등 구체적 수치는 반드시 포함

---

## 사용자 Q&A 처리

사용자가 요약된 논문에 대해 질문을 하면, 답변과 함께 해당 내용을 **요약 HTML에 반영**한다:

### 반영 방식
1. **관련 섹션에 삽입**: 질문이 특정 섹션과 직접 관련되면, 해당 섹션 끝에 Q&A 블록으로 추가
2. **개인 메모 섹션에 추가**: 특정 섹션에 귀속시키기 어렵거나 횡단적인 질문이면, 문서 끝의 "개인 메모" 섹션에 추가

### Q&A 형식 (HTML)
```html
<div class="qa-block">
  <p><strong>Q:</strong> 사용자 질문 내용</p>
  <p><strong>A:</strong> 답변 내용</p>
</div>
```

### 개인 메모 섹션
요약 HTML의 마지막 섹션으로 `<h2>개인 메모</h2>`를 배치한다:
- 최초 요약 생성 시에는 빈 상태로 생성 (내용 없이 헤더만)
- 사용자 Q&A, 추가 코멘트, 관련 아이디어 등을 누적 기록
- Q&A가 추가될 때 날짜를 함께 기록

### HTML 스타일 추가
Q&A 블록과 개인 메모 스타일은 이미 상단 CSS 템플릿에 포함되어 있다. 별도 추가 불필요.

---

## 파일 저장 규칙

- 요약 파일: `{YYYYMMDD}_{첫저자성}_{키워드}.html` (예: `20260223_vaswani_transformer.html`)
- 인덱스 파일: `index.html` (프로젝트 루트)
- 날짜는 요약을 생성하는 **오늘 날짜** 기준
- 저장 위치: 프로젝트 루트 디렉토리
- 가이드 파일: `guide.html` — CLAUDE.md 내용을 사용자 친화적 HTML로 렌더링한 페이지

### guide.html 동기화 규칙
- CLAUDE.md가 수정될 때마다 `guide.html`도 함께 업데이트한다
- guide.html은 CLAUDE.md의 주요 내용(프로젝트 개요, 입력 방법, 워크플로우, 요약 구조, 가이드라인, 정확성 기준 등)을 HTML로 렌더링한 페이지이다
- Claude Code 내부 구현 세부사항(에이전트 실행 방법, 템플릿 코드블록 등)은 제외하고, 사용자/독자 관점의 정보만 포함한다
- 하단에 마지막 업데이트 날짜를 기재한다
