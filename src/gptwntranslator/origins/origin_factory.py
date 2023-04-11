
from gptwntranslator.origins.base_origin import BaseOrigin
from gptwntranslator.origins.jjwxc_origin import JJWXCOrigin
from gptwntranslator.origins.kakuyomu_origin import KakuyomuOrigin
from gptwntranslator.origins.syosetu_ncode_origin import SyosetuNCodeOrigin
from gptwntranslator.origins.syosetu_novel18_origin import SyosetuNovel18Origin


class OriginFactory:
    @classmethod
    def origins(cls) -> dict:
        return {
            SyosetuNCodeOrigin.code: SyosetuNCodeOrigin,
            SyosetuNovel18Origin.code: SyosetuNovel18Origin,
            JJWXCOrigin.code: JJWXCOrigin,
            KakuyomuOrigin.code: KakuyomuOrigin,
        }
    
    @classmethod
    def origin_names(cls) -> dict:
        return {
            origin.code: origin.name for origin in cls.origins().values()
        }
    
    @classmethod
    def get_origin(cls, origin_name: str) -> BaseOrigin:
        if origin_name not in cls.origins():
            raise ValueError(f"Origin {origin_name} not found")
        return cls.origins()[origin_name]()
    
    def __init__(self) -> None:
        raise NotImplementedError("OriginFactory is a static class and should not be instantiated")

