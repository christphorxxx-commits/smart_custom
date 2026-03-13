from backend.app.common.core.core import tongyillm

for chunk in tongyillm.invoke("你是谁"):
    print(chunk)