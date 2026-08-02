# -*- coding: utf-8 -*-
"""
=============================================================
FreeCAD Python + AI 3D 설계 자동화 커리큘럼
Part 1 - Lesson 01: 첫 번째 큐브 (First Cube)
=============================================================

[실행 방법]
1. FreeCAD를 엽니다.
2. 상단 메뉴: Macro → Macros... → Create 를 클릭합니다.
3. 파일 이름을 "01_first_cube" 로 지정하고 OK를 누릅니다.
4. 에디터에 이 코드 전체를 붙여넣습니다.
5. 툴바의 ▶ Run 버튼(또는 F5)을 눌러 실행합니다.
6. 또는 Python 콘솔에서:
   exec(open("C:/Users/Administrator/Downloads/py/src/01_first_cube.py").read())

[학습 목표]
- FreeCAD 환경 확인 방법
- 문서(Document) 생성과 관리
- Part.makeBox() 로 큐브 생성
- 색상 변경 (ViewObject)
- 재료 속성 설정
- STL 파일로 내보내기
=============================================================
"""

# ============================================================
# 1. FreeCAD 환경 확인
# ============================================================
# FreeCAD Python 환경에서 실행 중인지 확인합니다.
# sys.modules 에 'FreeCAD' 가 있으면 FreeCAD 내부에서 실행 중입니다.

import sys
import os

# FreeCAD 모듈 임포트 시도
try:
    import FreeCAD
    import FreeCADGui
    import Part
    print("[INFO] FreeCAD 환경에서 실행 중입니다.")
    print(f"[INFO] FreeCAD 버전: {FreeCAD.Version()[0]}.{FreeCAD.Version()[1]}")
    print(f"[INFO] Python 버전: {sys.version}")
except ImportError:
    # FreeCAD 외부에서 실행된 경우 (일반 Python 스크립트)
    print("[ERROR] FreeCAD 모듈을 찾을 수 없습니다.")
    print("[ERROR] FreeCAD 내에서 실행해 주세요.")
    print("[ERROR] FreeCAD: https://www.freecad.org/downloads.php")
    sys.exit(1)

# ============================================================
# 2. 새 문서 생성
# ============================================================
# FreeCAD 의 모든 모델은 Document 안에 존재합니다.
# 기존에 열린 문서가 있다면 닫고 새 문서를 생성합니다.

# 현재 열린 문서가 있으면 닫기 (선택사항)
if FreeCAD.ActiveDocument:
    FreeCAD.closeDocument(FreeCAD.ActiveDocument.Name)
    print("[INFO] 기존 문서를 닫았습니다.")

# 새 문서 생성
doc = FreeCAD.newDocument("MyFirstCube")
print(f"[INFO] 새 문서 생성됨: '{doc.Name}'")

# ============================================================
# 3. 큐브 생성 — Part.makeBox()
# ============================================================
# Part.makeBox(가로, 세로, 높이) 는 원점(0,0,0)에서 시작하는
# 직육면체(Bounding Box)를 만듭니다.
# 단위는 FreeCAD 기본 단위인 밀리미터(mm)입니다.

cube_size = 10  # 10mm x 10mm x 10mm 정육면체

# makeBox() 로 쉐이프(Shape)를 만듭니다.
cube_shape = Part.makeBox(cube_size, cube_size, cube_size)
print(f"[INFO] 큐브 생성됨: {cube_size}mm x {cube_size}mm x {cube_size}mm")

# ============================================================
# 4. 문서에 파트(Part) 객체 추가
# ============================================================
# FreeCAD 문서에는 "FeaturePython" 또는 "Part::Feature" 객체를
# 추가하여 쉐이프를 시각화합니다.

# 새 파트 객체 생성
box_obj = doc.addObject("Part::Feature", "MyCube")

# 파트 객체에 쉐이프 할당
box_obj.Shape = cube_shape

# 문서 재computing — FreeCAD 내부 데이터를 갱신합니다.
doc.recompute()
print("[INFO] 문서 recomputed 완료")

# ============================================================
# 5. 색상 변경 (ViewObject)
# ============================================================
# FreeCAD 에서 각 파트의 시각적 속성은 ViewObject 로 제어합니다.
# ShapeColor, Transparency, DisplayMode 등을 변경할 수 있습니다.

# 색상 설정 (R, G, B) — 0.0 ~ 1.0 범위
# 빨간색 예시: (1.0, 0.0, 0.0)
box_obj.ViewObject.ShapeColor = (0.2, 0.6, 1.0)  # 파란색 계열

# 투명도 설정 (0 = 불투명, 1 = 완전 투명)
box_obj.ViewObject.Transparency = 20  # 20% 투명

# 디스플레이 모드 변경 (Shaded, Wireframe, Points 등)
box_obj.ViewObject.DisplayMode = "Shaded"

print("[INFO] 색상: 파란색 (0.2, 0.6, 1.0), 투명도: 20%")

# ============================================================
# 6. 재료 속성 설정 (선택사항)
# ============================================================
# FreeCAD 에서 재료 속성은 Part 객체의 Properties 에 설정할 수 있습니다.
# 여기서는 커스텀 속성을 추가하여 재료 정보를 메타데이터로 저장합니다.

# Density 속성 추가 (밀도, g/cm³)
box_obj.addProperty(
    "App::PropertyFloat",   # 속성 타입: 실수
    "Density",               # 속성 이름
    "Material",              # 속성 그룹
    "재료 밀도 (g/cm³)"       # 속성 설명
)
box_obj.Density = 7.85  # 강철의 밀도 (g/cm³)

# 재료 이름 속성 추가
box_obj.addProperty(
    "App::PropertyString",
    "MaterialName",
    "Material",
    "재료 이름"
)
box_obj.MaterialName = "Steel (강철)"

doc.recompute()
print("[INFO] 재료 속성 설정됨: 강철 (7.85 g/cm³)")

# ============================================================
# 7. 기본 치수 정보 출력
# ============================================================
# 생성된 큐브의 기본 속성을 확인합니다.

# 바운딩 박스 계산
bbox = box_obj.Shape.BoundBox
print(f"\n===== 큐브 정보 =====")
print(f"  위치: ({bbox.XMin:.1f}, {bbox.YMin:.1f}, {bbox.ZMin:.1f}) mm")
print(f"  크기: {bbox.XLength:.1f} x {bbox.YLength:.1f} x {bbox.ZLength:.1f} mm")
print(f"  부피: {box_obj.Shape.Volume:.2f} mm³")
print(f"  표면적: {box_obj.Shape.Area:.2f} mm²")
print(f"  무게: {box_obj.Shape.Volume * box_obj.Density / 1000:.2f} g")
print(f"======================\n")

# ============================================================
# 8. STL 파일로 내보내기
# ============================================================
# FreeCAD 에서 STL 파일을 내보내는 방법:
# 1. 객체를 선택
# 2. File → Export... 메뉴에서 STL 형식 선택
# 또는 Python 스크립트로 직접 내보내기

# 내보내기 경로 설정
export_dir = os.path.join(os.path.expanduser("~"), "Downloads", "py", "output")
os.makedirs(export_dir, exist_ok=True)  # 폴더가 없으면 생성

# STL 파일 경로
stl_filepath = os.path.join(export_dir, "my_first_cube.stl")

# FreeCAD 의 export 기능으로 STL 내보내기
# exportStl() 함수는 선택된 객체를 STL 형식으로 저장합니다.
box_obj.Shape.exportStl(stl_filepath)

print(f"[INFO] STL 파일 내보내기 완료: {stl_filepath}")

# ============================================================
# 9. STEP 파일도 함께 내보내기 (보너스)
# ============================================================
# STEP 형식은 다른 CAD 프로그램과 호환되는 범용 형식입니다.

step_filepath = os.path.join(export_dir, "my_first_cube.step")
box_obj.Shape.exportStep(step_filepath)
print(f"[INFO] STEP 파일 내보내기 완료: {step_filepath}")

# ============================================================
# 10. 뷰어에서 결과 확인
# ============================================================
# FreeCAD GUI가 실행 중이라면, 생성된 객체를 뷰어에 맞춰 Zoom 합니다.

try:
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
    print("[INFO] 뷰 전체 보기 (Fit All) 완료")
except:
    # GUI 없이 실행된 경우 (FreeCADCmd 등)
    print("[INFO] GUI 모드가 아닙니다. 뷰 조정을 건너뜁니다.")

# ============================================================
# 완료 메시지
# ============================================================
print("=" * 50)
print("  첫 번째 큐브 생성 완료!")
print("  축하합니다! FreeCAD Python 첫 걸음을 뗐습니다.")
print("=" * 50)
print("")
print("다음 단계: 02_cylinder.py — 원기둥 만들기")
print("")
