from uuid import uuid4

from .models import CanonicalCase, Clue, ImageBrief, Location, Suspect, VisualIdentity


def demo_case(genre: str = "AI laboratory sabotage") -> CanonicalCase:
    case_id = str(uuid4())
    identities = [
        VisualIdentity(approximate_age=34, hairstyle="단정한 단발", hair_color="검정", clothing="먹색 연구복", distinguishing_non_sensitive_visual_features="은색 사각 안경", portrait_description="차분한 연구 책임자, 날카로운 시선"),
        VisualIdentity(approximate_age=41, hairstyle="짧게 넘긴 머리", hair_color="짙은 갈색", clothing="남색 보안 재킷", distinguishing_non_sensitive_visual_features="낡은 손목시계", portrait_description="피곤한 보안 관리자, 굳은 표정"),
        VisualIdentity(approximate_age=29, hairstyle="긴 포니테일", hair_color="검정", clothing="검정 후디와 출입증", distinguishing_non_sensitive_visual_features="붉은 노트", portrait_description="긴장한 데이터 엔지니어, 관찰하는 눈빛"),
    ]
    suspects = [
        Suspect(id="seo", name="서민아", role="수석 연구원", public_profile="프로젝트의 모델 안전성 책임자", personality="정확하고 방어적", actual_alibi="22:48부터 세미나실에서 원격 회의", claimed_alibi="22:40부터 계속 세미나실에 있었다", private_knowledge=["감사 로그의 8분 공백", "윤재가 백업 키를 복제했다"], known_facts=["서버실은 백업 키로도 열린다", "실험 모델은 23시에 자동 배포된다"], lies=["22:40부터 회의 중이었다"], visual_identity=identities[0]),
        Suspect(id="yoon", name="윤재호", role="야간 보안 관리자", public_profile="시설 출입과 CCTV를 관리", personality="무뚝뚝하고 원칙적", actual_alibi="22:55 서버실에 침입해 안전장치를 제거", claimed_alibi="22:30부터 로비 순찰 중이었다", private_knowledge=["CCTV를 10분 반복 재생했다", "복제한 백업 키를 사용했다"], known_facts=["동쪽 복도 카메라는 수리 중이었다", "서민아가 늦게 회의에 들어갔다"], lies=["로비를 떠나지 않았다", "백업 키는 금고에 있다"], visual_identity=identities[1]),
        Suspect(id="han", name="한소진", role="데이터 엔지니어", public_profile="학습 데이터와 배포 파이프라인 담당", personality="솔직하지만 불안함", actual_alibi="22:50부터 카페에서 배달 기사와 대화", claimed_alibi="카페에서 야식을 기다렸다", private_knowledge=["윤재의 출입증이 두 번 찍힌 것을 봤다"], known_facts=["로그는 삭제되어도 체크섬이 남는다", "서민아의 회의 접속 시각은 22:48이다"], lies=[], visual_identity=identities[2]),
    ]
    locations = [
        Location(id="lobby", name="유리 로비", description="빗물이 흐르는 유리벽과 보안 데스크. 밤 근무의 흔적이 남아 있다."),
        Location(id="lab", name="메인 연구실", description="꺼진 단말과 붉은 비상등 아래 실험 기록이 흩어져 있다."),
        Location(id="cafe", name="직원 카페", description="식은 커피와 배달 영수증, 창밖의 비가 시간을 증언한다."),
        Location(id="server", name="격리 서버실", description="냉각 팬 소리 사이로 안전장치가 제거된 랙이 보인다.", locked=True, unlock_clue_id="key-log"),
    ]
    clues = [
        Clue(id="key-log", title="백업 키 출입 기록", category="access", location_id="lobby", target="보안 데스크 출입 로그", critical=True, player_description="22:55, 백업 키 B-02가 서버실을 열었다.", canonical_significance="윤재호가 복제한 키로 범행 장소에 들어갔다.", visual_asset_id="evidence-key-log"),
        Clue(id="cctv-loop", title="반복된 CCTV 프레임", category="cctv", location_id="lobby", target="CCTV", critical=True, prerequisites=["key-log"], player_description="22:52~23:02 화면 속 빗방울이 똑같이 반복된다.", canonical_significance="윤재호가 순찰 알리바이를 만들기 위해 영상을 반복했다.", visual_asset_id="evidence-cctv"),
        Clue(id="checksum", title="삭제 로그 체크섬", category="digital", location_id="lab", target="노트북 로그", critical=True, player_description="안전장치 설정 파일이 22:57 윤재호 계정으로 변경됐다.", canonical_significance="범행 계정과 정확한 조작 시각을 확정한다.", visual_asset_id="evidence-checksum"),
        Clue(id="meeting", title="회의 접속 기록", category="alibi", location_id="lab", target="회의 단말", player_description="서민아는 주장보다 8분 늦은 22:48에 접속했다.", canonical_significance="거짓말이지만 범행 시각에는 회의 중이었다."),
        Clue(id="receipt", title="배달 영수증", category="alibi", location_id="cafe", target="테이블", player_description="22:54 결제, 배달 기사 확인 서명이 있다.", canonical_significance="한소진의 알리바이를 보강한다."),
        Clue(id="watch", title="멈춘 손목시계 사진", category="personal", location_id="cafe", target="붉은 노트", red_herring=True, player_description="윤재호의 시계가 22:50에 멈춘 사진. 오래된 고장 기록도 있다.", canonical_significance="수상해 보이지만 범행과 무관하다."),
        Clue(id="relay", title="분리된 안전 릴레이", category="physical", location_id="server", target="서버 랙", critical=True, prerequisites=["key-log"], player_description="도구 자국에 보안팀 지급 드라이버의 파란 도료가 남았다.", canonical_significance="윤재호가 물리적으로 안전장치를 제거했다.", visual_asset_id="evidence-relay"),
    ]
    briefs = [ImageBrief(id="cover", asset_type="cover", subject="폭우 속 유리 연구동", environment="도시 외곽 AI 연구소", visual_description="붉은 비상등과 젖은 유리, 인물 없는 사건 현장")]
    briefs += [ImageBrief(id=f"suspect-{s.id}", asset_type="suspect", subject=s.name, environment="어두운 조사실", visual_description=s.visual_identity.portrait_description, continuity_notes=s.visual_identity.model_dump_json()) for s in suspects]
    briefs += [ImageBrief(id=f"location-{loc.id}", asset_type="location", subject=loc.name, environment=loc.description, visual_description="사실적이고 단서가 과장되지 않은 범죄 현장") for loc in locations]
    briefs += [ImageBrief(id=c.visual_asset_id, asset_type="evidence", subject=c.title, environment=c.location_id, visual_description=c.player_description, prohibited_details=["범인 이름", "정답 표시"]) for c in clues if c.visual_asset_id]
    return CanonicalCase(id=case_id, title="블랙아웃 프로토콜", genre=genre, introduction="폭우가 연구동을 고립시킨 밤, 공개 직전의 안전 모델이 파괴됐다.", incident_summary="23:02, 격리 서버의 안전장치가 제거되며 18개월의 연구가 손상됐다. 내부자 세 명만 접근할 수 있었다.", culprit_id="yoon", motive="보안 결함 은폐 계약을 지키고 감사에서 자신의 과실을 숨기기 위해", crime_time="22:55–23:02", crime_method="복제 백업 키로 서버실에 진입해 CCTV를 반복 재생하고 안전 릴레이를 분리", canonical_timeline=["22:48 서민아가 원격 회의에 접속", "22:50 한소진이 카페에서 배달 기사를 만남", "22:52 윤재호가 로비 CCTV 반복 재생 시작", "22:55 백업 키 B-02로 서버실 개방", "22:57 안전장치 설정 변경", "23:02 모델 손상 경보 발생"], solution_summary="윤재호는 CCTV 반복 영상으로 순찰 알리바이를 만들고 복제 키와 보안 도구로 서버를 파괴했다.", suspects=suspects, locations=locations, clues=clues, image_briefs=briefs)
