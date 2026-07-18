#!/usr/bin/env python3
"""
6축 로봇 암 감속기 모델링 스크립트
FreeCAD 1.1.1 호환

감속기 사양:
- 1축: 하모닉 드라이브 (CSF-14-100) - 감속비 100:1
- 2축: 하모닉 드라이브 (CSF-17-100) - 감속비 100:1
- 3축: 사이클로이드 감속기 (RV-20E) - 감속비 80:1
- 4축: 하모닉 드라이브 (CSF-11-80) - 감속비 80:1
- 5축: 사이클로이드 감속기 (RV-8E) - 감속비 51:1
- 6축: 하모닉 드라이브 (CSF-8-50) - 감속비 50:1
"""

import FreeCAD
import Part
import math
from FreeCAD import Base, Vector

class HarmonicReducer:
    """하모닉 드라이브 감속기 클래스"""
    
    def __init__(self, name, outer_diameter, length, reduction_ratio):
        self.name = name
        self.outer_diameter = outer_diameter
        self.length = length
        self.reduction_ratio = reduction_ratio
        
    def create_model(self):
        """하모닉 드라이브 모델 생성"""
        # 외부 하우징 (실린더)
        housing = Part.makeCylinder(
            self.outer_diameter / 2,
            self.length,
            Base.Vector(0, 0, 0),
            Base.Vector(0, 0, 1)
        )
        
        # 내부 웨이브 생성기 (실린더)
        inner_radius = self.outer_diameter / 2 * 0.6
        wave_generator = Part.makeCylinder(
            inner_radius,
            self.length * 0.8,
            Base.Vector(0, 0, self.length * 0.1),
            Base.Vector(0, 0, 1)
        )
        
        # 플렉스 spline (토러스 형상)
        flex_spline_radius = self.outer_diameter / 2 * 0.85
        flex_spline = Part.makeTorus(
            flex_spline_radius,
            self.outer_diameter / 2 * 0.05,
            Base.Vector(0, 0, self.length / 2),
            Base.Vector(0, 0, 1)
        )
        
        # 모델 조합
        model = housing.fuse(wave_generator).fuse(flex_spline)
        
        return model


class CycloidalReducer:
    """사이클로이드 감속기 클래스"""
    
    def __init__(self, name, outer_diameter, length, reduction_ratio):
        self.name = name
        self.outer_diameter = outer_diameter
        self.length = length
        self.reduction_ratio = reduction_ratio
        
    def create_model(self):
        """사이클로이드 감속기 모델 생성"""
        # 외부 링 (하우징)
        outer_ring = Part.makeCylinder(
            self.outer_diameter / 2,
            self.length,
            Base.Vector(0, 0, 0),
            Base.Vector(0, 0, 1)
        )
        
        # 사이클로이드 디스크 (원형 디스크)
        disc_radius = self.outer_diameter / 2 * 0.7
        disc = Part.makeCylinder(
            disc_radius,
            self.length * 0.6,
            Base.Vector(0, 0, self.length * 0.2),
            Base.Vector(0, 0, 1)
        )
        
        # 출력 샤프트
        shaft_radius = self.outer_diameter / 2 * 0.2
        shaft = Part.makeCylinder(
            shaft_radius,
            self.length * 1.2,
            Base.Vector(0, 0, -self.length * 0.1),
            Base.Vector(0, 0, 1)
        )
        
        # 베어링 (토러스)
        bearing = Part.makeTorus(
            self.outer_diameter / 2 * 0.75,
            self.outer_diameter / 2 * 0.04,
            Base.Vector(0, 0, self.length / 2),
            Base.Vector(0, 0, 1)
        )
        
        # 모델 조합
        model = outer_ring.fuse(disc).fuse(shaft).fuse(bearing)
        
        return model


def create_robot_arm_reducers():
    """6축 로봇 암 감속기 모델 생성"""
    
    # 감속기 사양 정의
    reducers_spec = {
        'axis1': {
            'name': '1축_하모닉',
            'type': 'harmonic',
            'outer_diameter': 50,  # mm
            'length': 40,          # mm
            'reduction_ratio': 100
        },
        'axis2': {
            'name': '2축_하모닉',
            'type': 'harmonic',
            'outer_diameter': 60,  # mm
            'length': 50,          # mm
            'reduction_ratio': 100
        },
        'axis3': {
            'name': '3축_사이클로이드',
            'type': 'cycloidal',
            'outer_diameter': 70,  # mm
            'length': 45,          # mm
            'reduction_ratio': 80
        },
        'axis4': {
            'name': '4축_하모닉',
            'type': 'harmonic',
            'outer_diameter': 40,  # mm
            'length': 35,          # mm
            'reduction_ratio': 80
        },
        'axis5': {
            'name': '5축_사이클로이드',
            'type': 'cycloidal',
            'outer_diameter': 35,  # mm
            'length': 30,          # mm
            'reduction_ratio': 51
        },
        'axis6': {
            'name': '6축_하모닉',
            'type': 'harmonic',
            'outer_diameter': 30,  # mm
            'length': 25,          # mm
            'reduction_ratio': 50
        }
    }
    
    # FreeCAD 문서 생성
    doc = FreeCAD.newDocument("RobotArmReducers")
    
    # 각 축별 감속기 생성
    for axis, spec in reducers_spec.items():
        print(f"\n{spec['name']} 감속기 생성 중...")
        print(f"  유형: {spec['type']}")
        print(f"  외경: {spec['outer_diameter']}mm")
        print(f"  길이: {spec['length']}mm")
        print(f"  감속비: {spec['reduction_ratio']}:1")
        
        if spec['type'] == 'harmonic':
            reducer = HarmonicReducer(
                spec['name'],
                spec['outer_diameter'],
                spec['length'],
                spec['reduction_ratio']
            )
        else:
            reducer = CycloidalReducer(
                spec['name'],
                spec['outer_diameter'],
                spec['length'],
                spec['reduction_ratio']
            )
        
        # 모델 생성 및 문서에 추가
        model = reducer.create_model()
        obj = doc.addObject("Part::Feature", spec['name'])
        obj.Shape = model
    
    # 문서 저장
    FreeCAD.ActiveDocument.recompute()
    
    print("\n" + "="*50)
    print("6축 로봇 암 감속기 모델링 완료!")
    print("="*50)
    print("\n생성된 감속기 목록:")
    for axis, spec in reducers_spec.items():
        print(f"  {spec['name']}: {spec['type']} ({spec['outer_diameter']}mm)")
    
    print("\nFreeCAD에서 모델을 확인하세요.")
    print("파일 저장: File -> Save As -> RobotArmReducers.FCStd")
    
    return doc


def print_reducer_specifications():
    """감속기 사양 출력"""
    print("\n" + "="*60)
    print("6축 로봇 암 감속기 사양표")
    print("="*60)
    print(f"{'축':<5} {'유형':<12} {'모델':<15} {'외경(mm)':<10} {'길이(mm)':<10} {'감속비':<8}")
    print("-"*60)
    
    specs = [
        ("1축", "하모닉", "CSF-14-100", 50, 40, "100:1"),
        ("2축", "하모닉", "CSF-17-100", 60, 50, "100:1"),
        ("3축", "사이클로이드", "RV-20E", 70, 45, "80:1"),
        ("4축", "하모닉", "CSF-11-80", 40, 35, "80:1"),
        ("5축", "사이클로이드", "RV-8E", 35, 30, "51:1"),
        ("6축", "하모닉", "CSF-8-50", 30, 25, "50:1"),
    ]
    
    for spec in specs:
        print(f"{spec[0]:<5} {spec[1]:<12} {spec[2]:<15} {spec[3]:<10} {spec[4]:<10} {spec[5]:<8}")
    
    print("-"*60)
    print("\n총 감속기 수: 6개")
    print("  - 하모닉 드라이브: 4개 (1, 2, 4, 6축)")
    print("  - 사이클로이드 감속기: 2개 (3, 5축)")


if __name__ == "__main__":
    print_reducer_specifications()
    print("\nFreeCAD에서 스크립트를 실행하세요.")
    print("FreeCAD -> Macros -> Run Macro -> robot_arm_reducer.py")