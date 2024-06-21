JSONValue = str | int | float | bool | None
JSONDict = dict[str, "JSONType"]
JSONArray = list["JSONType"]
JSONType = JSONValue | JSONDict | JSONArray
