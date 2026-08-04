# 옴니휠 로봇 CAD·PCB 통합 설계 교육

본 프로젝트는 **옴니휠(Omni-wheel) 로봇의 기구부**를 **FreeCAD**로 설계하고,
기구 도면을 활용하여 **EasyEDA**로 PCB를 설계한 뒤 **최종 3D 데이터까지 통합**하는
전 과정을 학습하기 위한 교육 커리큘럼입니다.

- 설계 도구: FreeCAD 1.1.3
   - [설치](https://github.com/FreeCAD/FreeCAD/releases/download/1.1.3/FreeCAD_1.1.3-Windows-x86_64-py311-installer.exe)
   - [포텀블](https://github.com/FreeCAD/FreeCAD/releases/download/1.1.3/FreeCAD_1.1.3-Windows-x86_64-py311.7z)
- PCB 도구: EasyEDA (Pro/Standard)
- 설계 목표: 옴니휠 로봇 전장 하우징 + 제어 PCB 3D 통합

---

## 📚 커리큘럼 구성

| 순서 | 파일 | 내용 |
| ---- | ---- | ---- |
| 01 | [01_설치_및_환경설정.md](01_설치_및_환경설정.md) | FreeCAD 설치, 한글화, 환경 설정, 작업대(Workbench) 이해 |
| 02 | [02_기초_설계.md](02_기초_설계.md) | 스케처(Sketcher)와 파트디자인(Part Design) 기초 설계 |
| 03 | [03_어셈블리.md](03_어셈블리.md) | 어셈블리(Assembly) 워크벤치 교육 |
| 04 | [04_판금.md](04_판금.md) | 판금(Sheet Metal) 워크벤치 교육 |
| 05 | [05_옴니휠_로봇_적용.md](05_옴니휠_로봇_적용.md) | 옴니휠 로봇 기구부 실무 적용 실습 |
| 06 | [06_EasyEDA_통합.md](06_EasyEDA_통합.md) | EasyEDA를 통한 PCB 설계 및 3D 통합 |

> 📌 초보자라면 **01 → 02 → 03 → 04** 순서로 학습한 뒤, **05 → 06** 순서로
> 실제 옴니휠 로봇 프로젝트에 적용하시기 바랍니다.

---

## 🛠 필수 설치 항목

| 구분 | 항목 | 버전 |
| ---- | ---- | ---- |
| 3D CAD | FreeCAD | 1.1.1 (Windows x86_64) |
| PCB EDA | EasyEDA | 최신 (무료) |
| (선택) | STEP 파일 뷰어 | 무관 |

### FreeCAD 실행 경로

- 설치 방식: **Portable (압축 해제식)**
- 실행 파일: `C:\Users\Administrator\Downloads\FreeCAD_1.1.1-Windows-x86_64-py311\bin\FreeCAD.exe`
- 작업 파일 저장 위치: `C:\Users\Administrator\Desktop\ME`

> 💡 포터블 버전은 시스템 레지스트리를 변경하지 않으므로 설치 제거가 간편합니다.
> 폴더를 통째로 삭제하면 끝입니다. 다만 `bin\FreeCAD.exe` 바로가기(단축 아이콘)를
> 바탕화면에 만들어 두면 편리합니다.

---

## 🚀 학습 목표 (프로젝트 최종 산출물)

1. 옴니휠 로봇 **기구부 3D 모델** 완성
   - 상판/하판(베이스 플레이트), 중간 아크릴, 모터 브래킷, 센서 거치대, 배터리 홀더 등
2. **판금 부품** 설계 (전면/후면 패널, 슬롯 가공 치수 도출)
3. 기구부 치수를 반영한 **PCB 실장 보드** 설계 (EasyEDA)
4. **기구부 + PCB 통합 3D** 어셈블리에서 간섭(충돌) 검증
5. STEP/3D PDF 등 **제조 및 협업용 파일** 산출

---

## 📂 프로젝트 기존 파일 (참고)

`C:\Users\Administrator\Desktop\ME` 에 이미 설계된 부품 파일들이 있습니다.

| 파일명 | 내용 |
| ------ | ---- |
| `OMNI_WHEEL_ROBOT.FCStd` | 옴니휠 로봇 최상위 어셈블리 |
| `58mm_Plastic_Omni_Wheel.FCStd` | 58mm 옴니휠 |
| `RB35GM-Motor.FCStd` | RB35GM 모터 |
| `Bottom_Plate1/2.FCStd` | 하부 플레이트 |
| `Middle_Acrylic.FCStd` | 중간 아크릴 판 |
| `Front_SheetMetal.FCStd` | 전면 판금 |
| `LIDAR.FCStd`, `RP-lidar-A1.igs.FCStd` | LiDAR 센서 |
| `Jetson_Xavier_NX_Modul.FCStd` | Jetson Xavier NX 모듈 |
| `TOP_PCB.FCStd`, `TOP_PCB-?.dxf` | 상부 PCB 및 DXF |
| `7inch HDMI LCD (H).FCStd` | 7인치 HDMI LCD |
| 기타 센서 | `CO2_Gas_Sensor`, `GP2Y1023AU0F`, `HDC1080_CCS811`, `SharpIRsensor`, `ULTRA_GUARD` |

이 파일들은 각 장의 실습 예시로 활용합니다.

---

## 🔗 관련 워크벤치

| 워크벤치 | 목적 | 관련 장 |
| -------- | ---- | ------- |
| Sketcher | 2D 스케치 (구속조건) | 02 |
| Part Design | 3D 솔리드 파트 설계 | 02 |
| Assembly | 부품 조립 (구속조건) | 03 |
| Sheet Metal | 판금 설계 (벤딩, 플랫패턴) | 04 |
| TechDraw | 2D 도면 생성 | 02·04 |
| A2plus (추가) | 경량 어셈블리 (선택) | 03 |

---

## ✅ 학습 완료 체크리스트

- [ ] FreeCAD 실행 및 한글화 완료
- [ ] 스케치 → 솔리드 → 도면 순서 숙지
- [ ] 어셈블리 구속조건 이해
- [ ] 판금 벤딩/플랫패턴 생성 가능
- [ ] 기존 `OMNI_WHEEL_ROBOT.FCStd` 어셈블리를 열고 파트 수정 가능
- [ ] EasyEDA에서 PCB를 만들고 3D 모델을 FreeCAD로 가져올 수 있음
