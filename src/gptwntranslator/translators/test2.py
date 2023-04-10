from gptwntranslator.origins.syosetu_novel18_origin import SyosetuNovel18Origin

origin = SyosetuNovel18Origin()

code = "n5590ft"

novel = origin.process_novel(code)

print(novel)