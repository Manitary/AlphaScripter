from main import eloDict, get_single_ai_data

get_single_ai_data(["huns"] * 2, "best", list(eloDict.keys()), eloDict, 3)

# benchmarker("best","Shadow 3.1",300,['huns']*2)
