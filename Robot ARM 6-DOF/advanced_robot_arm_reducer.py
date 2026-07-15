#!/usr/bin/env python3
"""
6축 로봇 암 감속기 고급 모델링 스크립트
FreeCAD 1.1.1 호환

이 스크립트는 다음을 포함합니다:
1. 하모닉 드라이브 감속기 상세 모델
2. 사이클로이드 감속기 상세 모델
3. 6축 로봇 암 전체 조립 모델
"""

import FreeCAD
import Part
import math
from FreeCAD import Base, Vector


class DetailedHarmonicReducer:
    """상세 하모닉 드라이브 감속기"""
    
    def __init__(self, name, params):
        self.name = name
        self.outer_diameter = params['outer_diameter']
        self.length = params['length']
        self.reduction_ratio = params['reduction_ratio']
        self.input_shaft_diameter = params.get('input_shaft', 8)
        self.output_shaft_diameter = params.get('output_shaft', 12)
        
    def create_housing(self):
        """외부 하우징 생성"""
        # 메인 하우징
        housing = Part.makeCylinder(
            self.outer_diameter / 2,
            self.length,
            Base.Vector(0, 0, 0),
            Base.Vector(0, 0, 1)
        )
        
        # 내부 챔버 (빈 공간 표현을 위해)
        inner_diameter = self.outer_diameter * 0.85
        inner_chamber = Part.makeCylinder(
            inner_diameter / 2,
            self.length * 0.9,
            Base.Vector(0, 0, self.length * 0.05),
            Base.Vector(0, 0, 1)
        )
        
        # 하우징에서 내부 챔버 제거
        housing = housing.cut(inner_chamber)
        
        return housing
    
    def create_wave_generator(self):
        """웨이브 생성기 생성"""
        # 웨이브 생성기 하우징
        wave_gen = Part.makeCylinder(
            self.outer_diameter * 0.3,
            self.length * 0.7,
            Base.Vector(0, 0, self.length * 0.15),
            Base.Vector(0, 0, 1)
        )
        
        # 타원형 캠 (회전 축)
        cam = Part.makeCylinder(
            self.outer_diameter * 0.15,
            self.length * 0.8,
            Base.Vector(0, 0, self.length * 0.1),
            Base.Vector(0, 0, 1)
        )
        
        return wave_gen.fuse(cam)
    
    def create_flex_spline(self):
        """플렉스 스플라인 생성"""
        # 유연한 스플라인 (토러스 형상)
        flex_spline = Part.makeTorus(
            self.outer_diameter * 0.42,
            self.outer_diameter * 0.03,
            Base.Vector(0, 0, self.length / 2),
            Base.Vector(0, 0, 1)
        )
        
        return flex_spline
    
    def create_circular_spline(self):
        """원형 스플라인 생성"""
        # 외부 기어 (원형 스플라인)
        circular_spline = Part.makeCylinder(
            self.outer_diameter * 0.45,
            self.length * 0.3,
            Base.Vector(0, 0, self.length * 0.35),
            Base.Vector(0, 0, 1)
        )
        
        return circular_spline
    
    def create_input_shaft(self):
        """입력 샤프트 생성"""
        shaft = Part.makeCylinder(
            self.input_shaft_diameter / 2,
            self.length * 1.5,
            Base.Vector(0, 0, -self.length * 0.25),
            Base.Vector(0, 0, 1)
        )
        
        return shaft
    
    def create_output_shaft(self):
        """출력 샤프트 생성"""
        shaft = Part.makeCylinder(
            self.output_shaft_diameter / 2,
            self.length * 1.3,
            Base.Vector(0, 0, self.length * 0.85),
            Base.Vector(0, 0, 1)
        )
        
        return shaft
    
    def create_bearings(self):
        """베어링 생성"""
        bearings = []
        
        # 입력 베어링
        bearing1 = Part.makeTorus(
            self.outer_diameter * 0.25,
            self.outer_diameter * 0.02,
            Base.Vector(0, 0, self.length * 0.1),
            Base.Vector(0, 0, 1)
        )
        bearings.append(bearing1)
        
        # 출력 베어링
        bearing2 = Part.makeTorus(
            self.outer_diameter * 0.35,
            self.outer_diameter * 0.02,
            Base.Vector(0, 0, self.length * 0.9),
            Base.Vector(0, 0, 1)
        )
        bearings.append(bearing2)
        
        return bearings
    
    def create_model(self):
        """전체 하모닉 드라이브 모델 생성"""
        model_parts = []
        
        # 각 구성 요소 생성
        model_parts.append(self.create_housing())
        model_parts.append(self.create_wave_generator())
        model_parts.append(self.create_flex_spline())
        model_parts.append(self.create_circular_spline())
        model_parts.append(self.create_input_shaft())
        model_parts.append(self.create_output_shaft())
        
        # 베어링 추가
        model_parts.extend(self.create_bearings())
        
        # 모든 파트 결합
        final_model = model_parts[0]
        for part in model_parts[1:]:
            final_model = final_model.fuse(part)
        
        return final_model


class DetailedCycloidalReducer:
    """상세 사이클로이드 감속기"""
    
    def __init__(self, name, params):
        self.name = name
        self.outer_diameter = params['outer_diameter']
        self.length = params['length']
        self.reduction_ratio = params['reduction_ratio']
        self.input_shaft_diameter = params.get('input_shaft', 6)
        self.output_shaft_diameter = params.get('output_shaft', 10)
        
    def create_housing(self):
        """외부 하우징 생성"""
        housing = Part.makeCylinder(
            self.outer_diameter / 2,
            self.length,
            Base.Vector(0, 0, 0),
            Base.Vector(0, 0, 1)
        )
        
        return housing
    
    def create_cycloidal_disc(self):
        """사이클로이드 디스크 생성"""
        # 메인 디스크
        disc = Part.makeCylinder(
            self.outer_diameter * 0.65,
            self.length * 0.5,
            Base.Vector(0, 0, self.length * 0.25),
            Base.Vector(0, 0, 1)
        )
        
        return disc
    
    def create_output_mechanism(self):
        """출력 메커니즘 생성"""
        # 출력 플랜지
        output_flange = Part.makeCylinder(
            self.outer_diameter * 0.5,
            self.length * 0.2,
            Base.Vector(0, 0, self.length * 0.8),
            Base.Vector(0, 0, 1)
        )
        
        return output_flange
    
    def create_input_shaft(self):
        """입력 샤프트 생성"""
        shaft = Part.makeCylinder(
            self.input_shaft_diameter / 2,
            self.length * 1.4,
            Base.Vector(0, 0, -self.length * 0.2),
            Base.Vector(0, 0, 1)
        )
        
        return shaft
    
    def create_output_shaft(self):
        """출력 샤프트 생성"""
        shaft = Part.makeCylinder(
            self.output_shaft_diameter / 2,
            self.length * 1.2,
            Base.Vector(0, 0, self.length * 0.9),
            Base.Vector(0, 0, 1)
        )
        
        return shaft
    
    def create_bearings(self):
        """베어링 생성"""
        bearings = []
        
        # 입력 베어링
        bearing1 = Part.makeTorus(
            self.outer_diameter * 0.2,
            self.outer_diameter * 0.015,
            Base.Vector(0, 0, self.length * 0.15),
            Base.Vector(0, 0, 1)
        )
        bearings.append(bearing1)
        
        # 출력 베어링
        bearing2 = Part.makeTorus(
            self.outer_diameter * 0.4,
            self.outer_diameter * 0.015,
            Base.Vector(0, 0, self.length * 0.85),
            Base.Vector(0, 0, 1)
        )
        bearings.append(bearing2)
        
        return bearings
    
    def create_model(self):
        """전체 사이클로이드 감속기 모델 생성"""
        model_parts = []
        
        # 각 구성 요소 생성
        model_parts.append(self.create_housing())
        model_parts.append(self.create_cycloidal_disc())
        model_parts.append(self.create_output_mechanism())
        model_parts.append(self.create_input_shaft())
        model_parts.append(self.create_output_shaft())
        
        # 베어링 추가
        model_parts.extend(self.create_bearings())
        
        # 모든 파트 결합
        final_model = model_parts[0]
        for part in model_parts[1:]:
            final_model = final_model.fuse(part)
        
        return final_model


def create_robot_arm_assembly():
    """6축 로봇 암 전체 조립 모델"""
    
    # 감속기 사양 정의
    reducer_specs = {
        'axis1': {
            'name': '1축_하모닉',
            'type': 'harmonic',
            'outer_diameter': 50,
            'length': 40,
            'reduction_ratio': 100,
            'input_shaft': 8,
            'output_shaft': 12
        },
        'axis2': {
            'name': '2축_하모닉',
            'type': 'harmonic',
            'outer_diameter': 60,
            'length': 50,
            'reduction_ratio': 100,
            'input_shaft': 10,
            'output_shaft': 14
        },
        'axis3': {
            'name': '3축_사이클로이드',
            'type': 'cycloidal',
            'outer_diameter': 70,
            'length': 45,
            'reduction_ratio': 80,
            'input_shaft': 8,
            'output_shaft': 12
        },
        'axis4': {
            'name': '4축_하모닉',
            'type': 'harmonic',
            'outer_diameter': 40,
            'length': 35,
            'reduction_ratio': 80,
            'input_shaft': 6,
            'output_shaft': 10
        },
        'axis5': {
            'name': '5축_사이클로이드',
            'type': 'cycloidal',
            'outer_diameter': 35,
            'length': 30,
            'reduction_ratio': 51,
            'input_shaft': 6,
            'output_shaft': 8
        },
        'axis6': {
            'name': '6축_하모닉',
            'type': 'harmonic',
            'outer_diameter': 30,
            'length': 25,
            'reduction_ratio': 50,
            'input_shaft': 5,
            'output_shaft': 8
        }
    }
    
    # FreeCAD 문서 생성
    doc = FreeCAD.newDocument("RobotArmAssembly")
    
    # 각 축별 감속기 생성 및 배치
    axis_positions = {
        'axis1': Base.Vector(0, 0, 0),           # 베이스
        'axis2': Base.Vector(0, 0, 50),          # 어깨
        'axis3': Base.Vector(0, 0, 110),         # 팔꿈치
        'axis4': Base.Vector(0, 0, 160),         # 손목1
        'axis5': Base.Vector(0, 0, 200),         # 손목2
        'axis6': Base.Vector(0, 0, 235)          # 손목3
    }
    
    for axis, spec in reducer_specs.items():
        print(f"\n{spec['name']} 감속기 생성 중...")
        
        if spec['type'] == 'harmonic':
            reducer = DetailedHarmonicReducer(spec['name'], spec)
        else:
            reducer = DetailedCycloidalReducer(spec['name'], spec)
        
        # 모델 생성
        model = reducer.create_model()
        
        # 위치 설정
        position = axis_positions[axis]
        
        # FreeCAD 객체로 추가
        obj = doc.addObject("Part::Feature", spec['name'])
        obj.Shape = model
        obj.Placement.Base = position
    
    # 암 링크 (연결부) 생성
    print("\n로봇 암 링크 생성 중...")
    
    link_lengths = {
        'link1': 60,   # 베이스-어깨
        'link2': 50,   # 어깨-팔꿈치
        'link3': 50,   # 팔꿈치-손목1
        'link4': 40,   # 손목1-손목2
        'link5': 35    # 손목2-손목3
    }
    
    link_positions = {
        'link1': Base.Vector(0, 0, 45),
        'link2': Base.Vector(0, 0, 105),
        'link3': Base.Vector(0, 0, 155),
        'link4': Base.Vector(0, 0, 195),
        'link5': Base.Vector(0, 0, 230)
    }
    
    for link, length in link_lengths.items():
        # 링크 생성 (실린더)
        link_model = Part.makeCylinder(
            15,  # 링크 두께
            length,
            link_positions[link],
            Base.Vector(0, 0, 1)
        )
        
        obj = doc.addObject("Part::Feature", link)
        obj.Shape = link_model
    
    # 문서 재계산
    FreeCAD.ActiveDocument.recompute()
    
    print("\n" + "="*60)
    print("6축 로봇 암 조립 모델 생성 완료!")
    print("="*60)
    
    return doc


def print_detailed_specifications():
    """상세 감속기 사양 출력"""
    print("\n" + "="*70)
    print("6축 로봇 암 감속기 상세 사양표")
    print("="*70)
    
    specs = [
        {
            'axis': '1축',
            'type': '하모닉 드라이브',
            'model': 'CSF-14-100',
            'outer_diameter': 50,
            'length': 40,
            'reduction_ratio': 100,
            'input_shaft': 8,
            'output_shaft': 12,
            'torque_capacity': 54,  # Nm
            'max_speed': 3000  # rpm
        },
        {
            'axis': '2축',
            'type': '하모닉 드라이브',
            'model': 'CSF-17-100',
            'outer_diameter': 60,
            'length': 50,
            'reduction_ratio': 100,
            'input_shaft': 10,
            'output_shaft': 14,
            'torque_capacity': 107,
            'max_speed': 3000
        },
        {
            'axis': '3축',
            'type': '사이클로이드',
            'model': 'RV-20E',
            'outer_diameter': 70,
            'length': 45,
            'reduction_ratio': 80,
            'input_shaft': 8,
            'output_shaft': 12,
            'torque_capacity': 157,
            'max_speed': 2000
        },
        {
            'axis': '4축',
            'type': '하모닉 드라이브',
            'model': 'CSF-11-80',
            'outer_diameter': 40,
            'length': 35,
            'reduction_ratio': 80,
            'input_shaft': 6,
            'output_shaft': 10,
            'torque_capacity': 23,
            'max_speed': 3500
        },
        {
            'axis': '5축',
            'type': '사이클로이드',
            'model': 'RV-8E',
            'outer_diameter': 35,
            'length': 30,
            'reduction_ratio': 51,
            'input_shaft': 6,
            'output_shaft': 8,
            'torque_capacity': 39,
            'max_speed': 2500
        },
        {
            'axis': '6축',
            'type': '하모닉 드라이브',
            'model': 'CSF-8-50',
            'outer_diameter': 30,
            'length': 25,
            'reduction_ratio': 50,
            'input_shaft': 5,
            'output_shaft': 8,
            'torque_capacity': 7,
            'max_speed': 4000
        }
    ]
    
    # 테이블 헤더
    print(f"\n{'축':<5} {'유형':<12} {'모델':<12} {'외경':<8} {'길이':<8} {'감속비':<8} {'토크':<8} {'속도':<8}")
    print(f"{'':5} {'':12} {'':12} {'(mm)':<8} {'(mm)':<8} {'':8} {'(Nm)':<8} {'(rpm)':<8}")
    print("-"*70)
    
    # 각 축별 사양 출력
    for spec in specs:
        print(f"{spec['axis']:<5} {spec['type']:<12} {spec['model']:<12} "
              f"{spec['outer_diameter']:<8} {spec['length']:<8} "
              f"{spec['reduction_ratio']:<8} {spec['torque_capacity']:<8} "
              f"{spec['max_speed']:<8}")
    
    print("-"*70)
    
    # 요약 정보
    print("\n감속기 구성 요약:")
    print(f"  총 감속기 수: {len(specs)}개")
    
    harmonic_count = sum(1 for s in specs if s['type'] == '하모닉 드라이브')
    cycloidal_count = sum(1 for s in specs if s['type'] == '사이클로이드')
    
    print(f"  - 하모닉 드라이브: {harmonic_count}개 (1, 2, 4, 6축)")
    print(f"  - 사이클로이드 감속기: {cycloidal_count}개 (3, 5축)")
    
    # 성능 요약
    print("\n성능 요약:")
    total_torque = sum(s['torque_capacity'] for s in specs)
    max_speed = max(s['max_speed'] for s in specs)
    
    print(f"  전체 토크 용량: {total_torque} Nm")
    print(f"  최대 입력 속도: {max_speed} rpm")
    print(f"  전체 감속비 범위: 50:1 ~ 100:1")


def create_assembly_drawing():
    """조립도 생성 (2D 스케치)"""
    doc = FreeCAD.newDocument("AssemblyDrawing")
    
    # 기본 평면 생성
    plane = Part.makePlane(300, 300, Base.Vector(-150, -150, 0))
    
    obj = doc.addObject("Part::Feature", "DrawingPlane")
    obj.Shape = plane
    
    # 축 라인 생성 (점선 표현을 위해 얇은 실린더 사용)
    axis_lines = [
        ("X축", Base.Vector(-150, 0, 0), Base.Vector(300, 0, 0)),
        ("Y축", Base.Vector(0, -150, 0), Base.Vector(0, 300, 0)),
        ("Z축", Base.Vector(0, 0, -50), Base.Vector(0, 0, 300))
    ]
    
    for name, start, end in axis_lines:
        length = (end - start).Length
        direction = (end - start).normalize()
        
        line = Part.makeCylinder(
            0.5,  # 얇은 선
            length,
            start,
            direction
        )
        
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = line
    
    FreeCAD.ActiveDocument.recompute()
    
    return doc


if __name__ == "__main__":
    print("6축 로봇 암 감속기 모델링 스크립트")
    print("="*50)
    
    # 상세 사양 출력
    print_detailed_specifications()
    
    print("\n" + "="*50)
    print("FreeCAD에서 실행하는 방법:")
    print("1. FreeCAD 열기")
    print("2. Macros -> Macros... 클릭")
    print("3. 이 스크립트 파일 선택")
    print("4. Run 클릭")
    print("="*50)