# 경제시사 데일리

매일 아침 경제 시사만 골라 정리하는 정적 사이트입니다 (GitHub Pages).

- `index.html` — 페이지 전체(HTML·CSS·JS 한 파일)
- `data/editions.json` — 발행된 모든 호(최신순 배열)
- `scripts/add_edition.py` — 새 호 JSON 하나를 검증해 `data/editions.json`에 합칩니다

```
python3 scripts/add_edition.py /tmp/edition.json
```

기사 그림(`stories[].figure`)은 `bars`, `line`, `range`, `flow` 네 가지 형식을 지원하며 페이지가 SVG로 직접 그립니다.
