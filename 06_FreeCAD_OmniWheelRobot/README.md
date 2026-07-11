# FreeCAD 포터블 3D CAD — 터틀봇 기구 설계

## 개요

> 3D CAD 도구 FreeCAD(포터블)를 이용하여 **터틀봇(TurtleBot)** 의 기구부를 전면 설계한다.
> 총 **3일 / 21h** 과정 — 기구 설계 전주기(모델링→조립→해석→출력→최적화) 체험

## 사용 도구

| 도구 | 용도 | 다운로드 |
|------|------|---------|
| FreeCAD 1.1.1 | 3D CAD 모델링 (포터블) | https://github.com/FreeCAD/FreeCAD/releases/download/1.1.1/FreeCAD_1.1.1-Windows-x86_64-py311.7z |
| WinRAR / 7-Zip | 7z 압축 해제 | https://www.7-zip.org/ |
| Ultimaker Cura | 슬라이싱 (선택) | https://ultimaker.com/software/ultimaker-cura |

## 학습 구조

```
Day 1 (7h) — 모델링: 터틀봇 부품 설계
├── Step 1: FreeCAD 설치 + 인터페이스 (40min)
├── Step 2: 2D 스케치 완전 정복 (1h 20min)
├── Step 3: 3D 형상 만들기 — Pad/Pocket/Revolution (1h 30min)
├── Step 4: 터틀봇 바퀴 + 타이어 모델링 (1h)
├── Step 5: 터틀봇 베이스 플레이트 모델링 (1h 30min)
└── Step 6: 모터 마운트 + 볼 캐스터 브라켓 (1h)

Day 2 (7h) — 조립·해석·출력
├── Step 7: A2plus 조립 — 터틀봇 완성 (2h)
├── Step 8: LiDAR 마운트 + 상판 모델링 (1h)
├── Step 9: FEA 구조 해석 (1h 30min)
├── Step 10: STL 출력 + 슬라이싱 (1h)
├── Step 11: 3D프린터 출력 시연 (1h)
└── Step 12: 설계 리뷰 + 팀 발표 (30min)

Day 3 (7h) — 해석 심화: 동역학·최적화·검증
├── Step 13: 운동학(Kinematics) 해석 (1h)
├── Step 14: 간섭 검사 + 공차 분석 (1h 30min)
├── Step 15: Assembly4 동적 시뮬레이션 (1h 30min)
├── Step 16: 위상 최적화 — 경량화 설계 (1h 30min)
└── Step 17: 종합 보고서 + 기술 발표 (1h 30min)
```

## 터틀봇 부품 목록

| 부품명 | 개수 | 설명 |
|--------|------|------|
| Base Plate (하판) | 1 | 원형, Φ180mm, 두께 5mm |
| Top Plate (상판) | 1 | 원형, Φ160mm, 두께 3mm |
| Drive Wheel (구동바퀴) | 2 | Φ66mm × 25mm |
| Tire (타이어) | 2 | Φ66mm, 두께 3mm (고무 재질) |
| Motor Mount (모터 마운트) | 2 | N20 모터 장착 브라켓 |
| Ball Caster Bracket | 1 | Φ10mm 볼 캐스터 장착부 |
| LiDAR Mount | 1 | RPLiDAR A1 장착대 |
| Standoff (기둥) | 4~6 | 상판-하판 연결 지지대 |

## 참고 링크

- FreeCAD 공식 문서: https://wiki.freecad.org/
- TurtleBot3 Burger 치수: https://www.robotis.com/sub_product/Turtlebot3_Burger
- A2plus 워크벤치: https://github.com/kbwbe/A2plus
