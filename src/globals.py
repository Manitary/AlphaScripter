from src.config import CONFIG


OLD_PARAMETERS = {
    # ! Duplicate keys: EventType
    "ActionId": "-1;600;601;602;603;604;605;606;607;608;609;610;611;612;613;614;615;616;617;618;619;620;621;631",
    "Age": "0;1;2;3",
    "AllyPlayer": "1;2;3;4;5;6;7;8;my-player-number;target-player;focus-player;-101;-103;-108;-201",
    "AnyPlayer": "0;1;2;3;4;5;6;7;8;my-player-number;target-player;focus-player;-101;-102;-103;-104;-105;-106;-107;-108;-109;-110;-111;-201;-202;-203;-204;-205",
    "BuildingId": "10;12;14;18;19;20;30;31;32;45;47;49;51;68;70;71;82;84;86;87;101;103;104;109;116;129;130;131;132;133;137;141;142;153;209;210;276;463;464;465;481;482;483;498;562;563;564;565;584;585;586;587;598;611;612;613;614;615;616;618;619;620;621;624;625;626;712;713;714;715;716;717;718;719;734;1189;1251",
    "Civ": "0|18",
    "ClassId": "-1;900;901;902;903;904;905;906;907;908;909;910;911;912;913;914;915;918;919;920;921;922;923;927;930;932;933;935;936;939;942;943;944;947;949;951;952;954;955;958;959",
    "CmdId": "-1|10",
    "ColorId": "1|8",
    "Commodity": "0;1;2",
    "compareOp": ">=;<=;==;!=;c:>;c:>=;c:<;c:<=;c:==;c:!=;g:>;g:>=;g:<;g:<=;g:==;g:!=;s:>;s:>=;s:<;s:<=;s:==;s:!=;<;>",
    "ComputerAllyPlayer": "1;2;3;4;5;6;7;8;my-player-number;target-player;focus-player;-103",
    "CustomResource": "0;1;2;3;907;908;909;910;915;932;933;958",
    "difficulty": "0;1;2;3;4",
    "DiffParameterId": "0;1",
    "ElapsedTime": "1|120000",
    "EscrowState": "0|512",
    "ESPlayerStance": "0;1;3",
    "EventID": "0|255",
    # "EventType": "0",
    "EventType": "0;0",
    "ExploredState": "0;15;128",
    "FactId": "0|54",
    "FindPlayerMethod": "0;1;2;3",
    "GameType": "0;1;2;3;5;6;7;8",
    "GarrisonableUnitId": "35;422;548;545;141;481;482;612;483;82;79;234;236;235",
    "GoalId": "1|512",
    "GroupId": "0|9",
    "GroupType": "100|109",
    "Id": "0|32000",
    "IdleType": "0;1;2;3",
    "MapSize": "0|5",
    "MapType": "-1;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;25;26;27;28;29;30;31;32;33;34;35;36;37;38;39;40;41;42;43;44",
    "mathOp": "0|35",
    "MaxDistance": "-1|32767",
    "MaxGarrison": "-1|32767",
    "MinDistance": "-1|32767",
    "MinGarrison": "-1|32767",
    "ObjectData": "-1|82",
    "ObjectList": "0;1",
    "ObjectStatus": "0;2;3;4;5",
    "OnMainland": "-1;0;1",
    "OrderId": "-1;700;701;702;703;704;705;706;707;708;709;710;711;712;713;714;715;716;717;718;719;720;721;731",
    "Perimeter": "1;2",
    "PlacementType": "0;1;2;3",
    "PlayerId": "0|8",
    "PlayerStance": "0;1;2;3",
    "Point": "41|510",
    "PositionType": "0|13",
    "ProjectileType": "0|7",
    "ResearchState": "0;1;2;3",
    "Resource": "0;1;2;3",
    "ResourceAmount": "0|224",
    "SearchOrder": "0;1;2",
    "SearchSource": "1;2",
    "SharedGoalId": "1|256",
    "SignalId": "0|255",
    "SnValue": "-100|100",
    "2": "2;2",
    "SnId": "272;225;258;41;98;103;188;195;135;136;295;255;86;4;3;5;76;194;273;271;285;277;284;267;294;291;229;280;278;279;281;248;219;218;244;242;254;247;264;20;276;251;163;117;156;282;240;232;239;166;118;159;75;230;131;256;231;265;104;134;167;287;263;286;260;149;26;60;236;234;100;274;237;235;238;74;233;87;216;16;204;252;59;35;245;73;112;261;36;58;61;257;42;226;275;288;246;228;227;243;1;0;2;19;179;269;270;268;253;259;168;148;250;94;93;99;109;110;111;106;107;108;165;119;158;249;292;143;18;266;301;293;203;262;283;164;120;157;34",
    "StartingResources": "1;2;3",
    "State": "-1;0;1",
    "Strict": "0;1",
    "TauntId": "1|255",
    "Terrain": "0|41",
    "TimerId": "1|50",
    "TimerState": "0;1;2",
    "typeOp": "c:;g:;s:",
    "UnitId": "-299;-298;-297;-296;-295;-294;-293;-292;-291;-290;-289;-288;-287;-286;-285;-284;-283;-282;-281;-280;-279;-278;-277;-276;-275;-274;-273;-272;-271;-270;-269;-268;-267;-266;-265;-264;-1;4;5;6;7;8;11;13;17;21;24;25;35;36;38;39;40;41;42;46;56;57;73;74;75;77;83;93;106;114;118;120;122;123;124;125;128;156;183;184;185;203;204;207;208;212;214;216;218;220;222;223;230;232;239;250;259;260;279;280;281;282;283;286;291;293;329;330;331;354;358;359;418;420;422;440;441;442;448;453;459;467;473;474;492;494;527;528;529;530;531;532;533;534;539;542;545;546;548;553;554;555;556;557;558;559;560;561;567;569;579;581;588;590;592;653;691;692;694;701;725;726;732;751;752;753;755;757;759;760;761;762;763;765;766;771;773;774;775;782;784;811;823;827;829;830;831;832;836;861;866;868;869;871;873;875;876;878;879;881;882;886;887;891;900;901;902;903;904;905;906;907;908;909;910;911;912;913;914;915;918;919;920;921;922;923;927;930;932;933;935;936;939;942;943;944;947;949;951;952;954;955;958;959",
    "UnitIdStrict": "4;5;6;7;8;11;13;17;21;24;25;35;36;38;39;40;41;42;46;56;57;73;74;75;77;83;93;106;114;118;120;122;123;124;125;128;156;183;184;185;203;204;207;208;212;214;216;218;220;222;223;230;232;239;250;259;260;279;280;281;282;283;286;291;293;329;330;331;354;358;359;418;420;422;440;441;442;448;453;459;467;473;474;492;494;527;528;529;530;531;532;533;534;539;542;545;546;548;553;554;555;556;557;558;559;560;561;567;569;579;581;588;590;592;653;691;692;694;701;725;726;732;751;752;753;755;757;759;760;761;762;763;765;766;771;773;774;775;782;784;811;823;827;829;830;831;832;836;861;866;868;869;871;873;875;876;878;879;881;882;886;887;891",
    "value256": "0|255",
    "value32": "-32768|32767",
    "value32Positive": "1|32767",
    "Victory": "0;1;2;3;4",
    "WallId": "72;117;155;-399",
    "RuleId": "0|32767",
    "PriorityType": "0;1",
    "ResetMode": "0;1",
    "OnOff": "0;1",
    "ObjectId": "-299;-298;-297;-296;-295;-294;-293;-292;-291;-290;-289;-288;-287;-286;-285;-284;-283;-282;-281;-280;-279;-278;-277;-276;-275;-274;-273;-272;-271;-270;-269;-268;-267;-266;-265;-264;-1;4;5;6;7;8;11;13;17;21;24;25;35;36;38;39;40;41;42;46;56;57;73;74;75;77;83;93;106;114;118;120;122;123;124;125;128;156;183;184;185;203;204;207;208;212;214;216;218;220;222;223;230;232;239;250;259;260;279;280;281;282;283;286;291;293;329;330;331;354;358;359;418;420;422;440;441;442;448;453;459;467;473;474;492;494;527;528;529;530;531;532;533;534;539;542;545;546;548;553;554;555;556;557;558;559;560;561;567;569;579;581;588;590;592;653;691;692;694;701;725;726;732;751;752;753;755;757;759;760;761;762;763;765;766;771;773;774;775;782;784;811;823;827;829;830;831;832;836;861;866;868;869;871;873;875;876;878;879;881;882;886;887;891;900;901;902;903;904;905;906;907;908;909;910;911;912;913;914;915;918;919;920;921;922;923;927;930;932;933;935;936;939;942;943;944;947;949;951;952;954;955;958;959,10;12;14;18;19;20;30;31;32;45;47;49;51;68;70;71;82;84;86;87;101;103;104;109;116;129;130;131;132;133;137;141;142;153;209;210;276;463;464;465;481;482;483;498;562;563;564;565;584;585;586;587;598;611;612;613;614;615;616;618;619;620;621;624;625;626;712;713;714;715;716;717;718;719;734;1189;1251",
    "ScoutMethod": "0;1;2;3;4;5;6",
    "AttackStance": "0;1;2;3",
    "TargetAction": "0|18",
    "Formation": "-1;2;4;7;8",
    "0|240": "0|240",
    "0|40": "0|40",
    "0|239": "0|239",
    "83;293": "83;293",
    "-254|254": "-254|254",
    "-1|11": "-1|11",
    "0|100": "0|100",
    "-1|250": "-1|250",
    "1": "1|1",
    "GoalId2": "1|512",
    # "Trainable": "759;militiaman-line;spearman-line;battering-ram-line;mangonel-line;scorpion-line;villager;trebuchet;petard;5;monk;886;36;huskarl-line",
    "Trainable": "archer-line;cavalry-archer-line;skirmisher-line;militiaman-line;spearman-line;battering-ram-line;mangonel-line;scorpion-line;knight-line;scout-cavalry-line;tarkan-line;villager;trebuchet;petard;5;monk;886;36",
    "Buildable": "town-center;farm;house;mill;mining-camp;lumber-camp;dock;blacksmith;market;monastery;university;wonder;barracks;archery-range;stable;siege-workshop;outpost;castle;stone-wall;palisade-wall;gate",
    "TechId": "2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;19;21;22;23;24;27;34;35;37;39;45;47;48;49;50;51;52;54;55;59;60;61;63;64;67;68;74;75;76;77;80;81;82;83;90;93;96;98;100;101;102;103;140;182;194;197;199;200;201;202;203;207;209;211;212;213;215;217;218;219;221;222;230;231;233;236;237;239;244;246;249;252;254;255;257;264;265;278;279;280;315;316;319;320;321;322;360;361;362;363;364;365;366;367;368;369;370;371;372;373;374;375;376;377;379;380;398;408;428;429;432;434;435;436;437;438;439;440;441;445;448;450;457",
    # "TechId": "2;6;7;8;9;10;11;12;13;14;15;16;17;19;21;22;23;39;45;47;48;50;51;52;54;55;59;63;64;67;68;74;75;76;77;80;81;82;83;90;93;96;98;100;101;102;103;140;182;194;197;199;200;201;202;203;207;209;211;212;213;215;217;218;219;221;222;230;231;233;236;237;239;249;252;254;255;257;264;265;278;279;280;315;316;319;320;321;322;377;379;380;408;428;429;435;437;438;439;441;445;457",
    "0|10": "0|10",
    "0|200": "0|200",
    "0|50000": "0|50000",
    "0|50": "0|50",
    "0|20000": "0|20000",
    "0|170": "0|170",
    "14|1000": "14|1000",
    "25|1000": "25|1000",
}

PARAMETERS = {
    # ! Duplicate key: ActionId
    # "ActionId": "-1;600;601;602;603;604;605;606;607;608;609;610;611;612;613;615;616;617;618;619;620;631",
    "ActionId": "-1;600;601;602;603;604;605;606;607;608;609;610;611;612;613;614;615;616;617;618;619;620;621;631",
    "Age": "0;1;2;3",
    "AllyPlayer": "1;2;my-player-number;target-player;focus-player;-101;-103;-108;-201",
    "AnyPlayer": "0;1;2;my-player-number;target-player;focus-player;-101;-102;-103;-104;-105;-106;-107;-108;-109;-110;-111;-201;-202;-203;-204;-205",
    "BuildingId": "10;12;14;18;19;20;30;31;32;49;68;70;71;82;84;86;87;101;103;104;109;116;129;130;131;132;137;141;142;153;209;210;276;463;464;465;498;562;563;564;565;584;585;586;587;598;621",
    "Civ": "17",
    "ClassId": "-1;900;903;904;906;907;908;909;910;911;912;913;914;915;918;919;927;932;935;936;939;942;943;947;949;951;952;954;955;958",
    "CmdId": "0;1;2;3;4;5;6;8;10",
    "ColorId": "1|8",
    "Commodity": "0;1;2",
    "compareOp": ">;>=;<;<=;==;!=;c:>;c:>=;c:<;c:<=;c:==;c:!=;g:>;g:>=;g:<;g:<=;g:==;g:!=;s:>;s:>=;s:<;s:<=;s:==;s:!=",
    "ComputerAllyPlayer": "1;2;my-player-number;target-player;focus-player;-103",
    "CustomResource": "0;1;2;3;907;908;909;910;915;932;958",
    "difficulty": "4",
    "DiffParameterId": "0;1",
    "ElapsedTime": "1|120000",
    "EscrowState": "0|512",
    "ESPlayerStance": "0;1;3",
    "EventID": "0",
    "EventType": "0",
    "ExploredState": "0;15;128",
    "FactId": "0|54",
    "FindPlayerMethod": "0;1;2;3",
    "GameType": "0",
    "GarrisonableUnitId": "35;422;548;109;71;141;142;621;82;79",
    "GoalId": "1|512",
    "GroupId": "0|9",
    "GroupType": "100;101;108",
    "Id": "1|512",
    "IdleType": "0;1",
    "MapSize": "0",
    "MapType": "21",
    "mathOp": "0|35",
    "MaxDistance": "-1|204",
    "MaxGarrison": "-1|20",
    "MinDistance": "-1|204",
    "MinGarrison": "-1|20",
    "ObjectData": "-1|82",
    "ObjectList": "0;1",
    "ObjectStatus": "0;2;3;4;5",
    "OnMainland": "-1;0;1",
    "OrderId": "-1;700;701;702;703;704;705;706;707;708;709;710;711;712;713;714;715;716;717;718;719;720;721;731",
    "Perimeter": "1;2",
    "PlacementType": "0;1;2;3",
    "PlayerId": "0|2",
    "PlayerStance": "0;1;2;3",
    "Point": "41|510",
    "PositionType": "0|13",
    "ProjectileType": "0|7",
    "ResearchState": "0;1;2;3",
    "Resource": "0|7",
    "ResourceAmount": "0;1;2;3;4;6;7;11;12;20;21;22;27;32;34;35;36;37;40;41;42;43;44;45;48;50;55;66;67;69;70;77;78;80;81;98;99;100;101;102;103;110;111;118;119;126;127;134;136;137;144;145;152;153;154;155;156;157;164;165;166;167;168;169;170;171;172;173;174;175;178;179;183;184;185;186;187;188;192;193;196;197",
    "SearchOrder": "0;1;2",
    "SearchSource": "1;2",
    "SharedGoalId": "1|256",
    "SignalId": "0",
    "SnId": "272;225;258;41;98;103;188;195;135;136;295;255;86;4;3;5;76;194;273;271;285;277;284;267;294;291;229;280;278;279;281;248;219;218;244;242;254;247;264;20;276;251;163;117;156;282;240;232;239;166;118;159;75;230;131;256;231;265;104;134;167;287;263;286;260;149;26;60;236;234;100;274;237;235;238;74;233;87;216;16;204;252;59;35;245;73;112;261;36;58;61;257;42;226;275;288;246;228;227;243;1;0;2;19;179;269;270;268;253;259;168;148;250;94;93;99;109;110;111;106;107;108;165;119;158;249;292;143;18;266;301;293;203;262;283;164;120;157;34",
    "StartingResources": "1",
    "State": "-1;0;1",
    "Strict": "0;1",
    "TauntId": "1|255",
    "TechId": "2;8;13;14;15;19;21;22;39;45;47;48;50;54;55;67;68;74;75;76;80;81;82;90;93;96;98;100;101;102;103;182;197;199;200;201;202;203;207;209;211;212;213;215;217;218;221;222;231;233;249;252;254;255;265;278;280;315;319;321;322;408;428;429;435;436;437;439",
    "Terrain": "0|41",
    "TimerId": "1|50",
    "TimerState": "0;1;2",
    "typeOp": "c:;g:;s:",
    "UnitId": "-299;-298;-297;-296;-295;-291;-290;-289;-287;-286;-265;-1;4;6;7;24;35;38;39;42;56;57;74;75;77;83;93;118;120;122;123;124;125;128;156;204;212;214;216;218;220;222;259;279;280;283;286;293;331;354;358;359;422;440;441;448;473;474;546;548;569;579;581;590;592;755;757;886;887;900;903;904;906;907;908;909;910;911;912;913;914;915;918;919;927;932;935;936;939;942;943;947;949;951;952;954;955;958",
    "UnitIdStrict": "4;6;7;24;35;38;39;42;56;57;74;75;77;83;93;118;120;122;123;124;125;128;156;204;212;214;216;218;220;222;259;279;280;283;286;293;331;354;358;359;422;440;441;448;473;474;546;548;569;579;581;590;592;755;757;886;887",
    "value256": "0|255",
    "value32": "-32768|32767",
    "value32Positive": "1|32767",
    "Victory": "1",
    "WallId": "72;117;155;-399",
    "RuleId": "0|32767",
    "PriorityType": "0;1",
    "ResetMode": "0;1",
    "OnOff": "0;1",
    "ObjectId": "-299;-298;-297;-296;-295;-291;-290;-289;-287;-286;-265;-1;4;6;7;24;35;38;39;42;56;57;74;75;77;83;93;118;120;122;123;124;125;128;156;204;212;214;216;218;220;222;259;279;280;283;286;293;331;354;358;359;422;440;441;448;473;474;546;548;569;579;581;590;592;755;757;886;887;900;903;904;906;907;908;909;910;911;912;913;914;915;918;919;927;932;935;936;939;942;943;947;949;951;952;954;955;958;10;12;14;18;19;20;30;31;32;49;68;70;71;82;84;86;87;101;103;104;109;116;129;130;131;132;137;141;142;153;209;210;276;463;464;465;498;562;563;564;565;584;585;586;587;598;621",
    "ScoutMethod": "0;1;2;3;4;5;6",
    "AttackStance": "0;1;2;3",
    "TargetAction": "0|18",
    "Formation": "-1;2;4;7;8",
    "SnValue": "-100|100",
    "2": "2;2",
    "0|240": "0|240",
    "0|40": "0|40",
    "0|239": "0|239",
    "83;293": "83;293",
    "-254|254": "-254|254",
    "-1|11": "-1|11",
    "0|100": "0|100",
    "-1|250": "-1|250",
    "1": "1|1",
    "GoalId2": "1|512",
    "Trainable": "archer-line;cavalry-archer-line;skirmisher-line;militiaman-line;spearman-line;battering-ram-line;mangonel-line;scorpion-line;knight-line;scout-cavalry-line;tarkan-line;villager;trebuchet;petard;5;monk;886;36",
    "Buildable": "town-center;farm;house;mill;mining-camp;lumber-camp;dock;blacksmith;market;monastery;university;wonder;barracks;archery-range;stable;siege-workshop;outpost;castle;stone-wall;palisade-wall;gate;watch-tower;guard-tower;keep",
    "0|10": "0|10",
    "0|200": "0|200",
    "0|50000": "0|50000",
    "0|50": "0|50",
    "0|20000": "0|20000",
    "0|170": "0|170",
    "14|1000": "14|1000",
    "25|1000": "25|1000",
}

FACTS = {
    "attack-soldier-count": ["2", "compareOp", "0|200", "", ""],
    "building-available": ["1", "BuildingId", "", "", ""],
    "building-count": ["2", "compareOp", "0|50", "", ""],
    "building-count-total": ["2", "compareOp", "0|200", "", ""],
    "building-type-count": ["3", "BuildingId", "compareOp", "0|50", ""],
    "building-type-count-total": ["3", "BuildingId", "compareOp", "0|50", ""],
    "can-afford-building": ["1", "BuildingId", "", "", ""],
    "can-afford-complete-wall": ["2", "Perimeter", "WallId", "", ""],
    "can-afford-research": ["1", "TechId", "", "", ""],
    "can-afford-unit": ["1", "UnitId", "", "", ""],
    "can-build": ["1", "BuildingId", "", "", ""],
    "can-build-with-escrow": ["1", "BuildingId", "", "", ""],
    "can-build-gate": ["1", "Perimeter", "", "", ""],
    "can-build-gate-with-escrow": ["1", "Perimeter", "", "", ""],
    "can-build-wall": ["2", "Perimeter", "WallId", "", ""],
    "can-build-wall-with-escrow": ["2", "Perimeter", "WallId", "", ""],
    "can-buy-commodity": ["1", "Commodity", "", "", ""],
    "can-research": ["1", "TechId", "", "", ""],
    "can-research-with-escrow": ["1", "TechId", "", "", ""],
    "can-sell-commodity": ["1", "Commodity", "", "", ""],
    "can-spy": ["0", "", "", "", ""],
    "can-spy-with-escrow": ["0", "", "", "", ""],
    "can-train": ["1", "UnitId", "", "", ""],
    "can-train-with-escrow": ["1", "UnitId", "", "", ""],
    "civilian-population": ["2", "compareOp", "0|200", "", ""],
    "civ-selected": ["1", "Civ", "", "", ""],
    "commodity-buying-price": ["3", "Commodity", "compareOp", "25|1000", ""],
    "commodity-selling-price": ["3", "Commodity", "compareOp", "14|1000", ""],
    "current-age": ["1", "compareOp", "Age", "", ""],  # maybe cause issues
    "current-age-time": ["2", "compareOp", "0|20000", "", ""],
    "current-score": ["2", "compareOp", "0|50000", "", ""],
    "death-match-game": ["0", "", "", "", ""],
    "defend-soldier-count": ["2", "compareOp", "0|200", "", ""],
    "difficulty": ["2", "compareOp", "difficulty", "", ""],
    "doctrine": ["1", "value32", "", "", ""],
    "dropsite-min-distance": ["3", "Resource", "compareOp", "0|170", ""],
    "enemy-buildings-in-town": ["0", "", "", "", ""],
    "enemy-captured-relics": ["0", "", "", "", ""],
    "escrow-amount": ["3", "Resource", "compareOp", "0|50000", ""],
    "event-detected": ["2", "EventType", "EventID", "", ""],
    "false": ["0", "", "", "", ""],
    "food-amount": ["2", "compareOp", "0|50000", "", ""],
    "game-time": ["2", "compareOp", "0|20000", "", ""],
    "game-type": ["2", "compareOp", "GameType", "", ""],
    "gate-count": ["3", "Perimeter", "compareOp", "0|50", ""],
    "goal": ["2", "GoalId", "value32", "", ""],
    "gold-amount": ["2", "compareOp", "0|50000", "", ""],
    "hold-koh-ruin": ["0", "", "", "", ""],
    "hold-relics": ["0", "", "", "", ""],
    "housing-headroom": ["2", "compareOp", "0|200", "", ""],
    "idle-farm-count": ["2", "compareOp", "0|50", "", ""],
    "military-population": ["2", "compareOp", "0|200", "", ""],
    "player-computer": ["1", "AnyPlayer", "", "", ""],
    "player-human": ["1", "AnyPlayer", "", "", ""],
    "player-in-game": ["1", "AnyPlayer", "", "", ""],
    "player-number": ["1", "AnyPlayer", "", "", ""],
    "player-resigned": ["1", "AnyPlayer", "", "", ""],
    "player-valid": ["1", "AnyPlayer", "", "", ""],
    "players-building-count": ["3", "AnyPlayer", "compareOp", "0|50", ""],
    "players-building-type-count": [
        "4",
        "AnyPlayer",
        "BuildingId",
        "compareOp",
        "0|50",
    ],
    "players-civ": ["2", "AnyPlayer", "Civ", "", ""],
    "players-civilian-population": ["3", "AnyPlayer", "compareOp", "0|200", ""],
    "players-current-age": ["3", "AnyPlayer", "compareOp", "Age", ""],
    "players-current-age-time": ["3", "AnyPlayer", "compareOp", "0|20000", ""],
    "players-military-population": ["3", "AnyPlayer", "compareOp", "0|200", ""],
    "players-population": ["3", "AnyPlayer", "compareOp", "0|200", ""],
    "players-score": ["3", "AnyPlayer", "compareOp", "0|50000", ""],
    "players-stance": ["2", "AnyPlayer", "ESPlayerStance", "", ""],
    "players-unit-count": ["3", "AnyPlayer", "compareOp", "0|200", ""],
    "players-unit-type-count": ["4", "AnyPlayer", "UnitId", "compareOp", "0|200"],
    "population": ["2", "compareOp", "0|200", "", ""],
    "population-cap": ["2", "compareOp", "0|200", "", ""],
    "population-headroom": ["2", "compareOp", "0|200", "", ""],
    "random-number": ["2", "compareOp", "value32", "", ""],
    "research-available": ["1", "TechId", "", "", ""],
    "research-completed": ["1", "TechId", "", "", ""],
    "resource-found": ["1", "Resource", "", "", ""],
    "shared-goal": ["2", "SharedGoalId", "value32", "", ""],
    "sheep-and-forage-too-far": ["0", "", "", "", ""],
    "soldier-count": ["2", "compareOp", "0|200", "", ""],
    "stance-toward": ["2", "AnyPlayer", "ESPlayerStance", "", ""],
    "starting-age": ["2", "compareOp", "Age", "", ""],
    "starting-resources": ["2", "compareOp", "StartingResources", "", ""],
    "stone-amount": ["2", "compareOp", "0|50000", "", ""],
    "strategic-number": ["3", "SnId", "compareOp", "value32", ""],
    "timer-triggered": ["1", "TimerId", "", "", ""],
    "town-under-attack": ["0", "", "", "", ""],
    "true": ["0", "", "", "", ""],
    "unit-available": ["1", "UnitId", "", "", ""],
    "unit-count": ["2", "compareOp", "0|200", "", ""],
    "unit-count-total": ["2", "compareOp", "0|200", "", ""],
    "unit-type-count": ["3", "UnitId", "compareOp", "0|200", ""],
    "unit-type-count-total": ["3", "UnitId", "compareOp", "0|200", ""],
    "wall-completed-percentage": ["3", "Perimeter", "compareOp", "0|100", ""],
    "wall-invisible-percentage": ["3", "Perimeter", "compareOp", "0|100", ""],
    "wood-amount": ["2", "compareOp", "0|50000", "", ""],
    "up-add-object-by-id": ["3", "SearchSource", "typeOp", "Id", ""],
    "up-allied-goal": ["4", "ComputerAllyPlayer", "GoalId", "compareOp", "value32"],
    "up-allied-resource-amount": [
        "4",
        "AllyPlayer",
        "ResourceAmount",
        "compareOp",
        "value32",
    ],
    "up-allied-sn": ["4", "ComputerAllyPlayer", "SnId", "compareOp", "value32"],
    "up-attacker-class": ["2", "compareOp", "ClassId", "", ""],
    "up-building-type-in-town": ["4", "typeOp", "BuildingId", "compareOp", "0|50"],
    "up-can-build": ["3", "EscrowState", "typeOp", "BuildingId", ""],
    "up-can-build-line": ["4", "EscrowState", "Point", "typeOp", "BuildingId"],
    "up-can-research": ["3", "EscrowState", "typeOp", "TechId", ""],
    "up-can-search": ["1", "SearchSource", "", "", ""],
    "up-can-train": ["3", "EscrowState", "typeOp", "UnitId", ""],
    "up-compare-const": ["3", "value32", "compareOp", "value32", ""],
    "up-compare-goal": ["3", "GoalId", "compareOp", "value32", ""],
    "up-compare-sn": ["3", "SnId", "compareOp", "value32", ""],
    "up-defender-count": ["2", "compareOp", "0|200", "", ""],
    "up-enemy-buildings-in-town": ["2", "compareOp", "0|50", "", ""],
    "up-enemy-units-in-town": ["2", "compareOp", "0|200", "", ""],
    "up-enemy-villagers-in-town": ["2", "compareOp", "0|200", "", ""],
    "up-find-remote": ["4", "typeOp", "UnitId", "typeOp", "0|40"],
    "up-find-resource": ["4", "typeOp", "CustomResource", "typeOp", "0|240"],
    "up-find-status-remote": ["4", "typeOp", "UnitId", "typeOp", "0|240"],
    "up-gaia-type-count": ["4", "typeOp", "CustomResource", "compareOp", "0|200"],
    "up-gaia-type-count-total": [
        "4",
        "typeOp",
        "CustomResource",
        "compareOp",
        "0|200",
    ],
    "up-get-object-data": ["2", "ObjectData", "GoalId", "", ""],
    "up-get-object-target-data": ["2", "ObjectData", "GoalId", "", ""],
    "up-get-point-contains": ["4", "Point", "GoalId", "typeOp", "ObjectId"],
    "up-group-size": ["4", "typeOp", "GroupId", "compareOp", "0|200"],
    "up-idle-unit-count": ["3", "IdleType", "compareOp", "0|200", ""],
    "up-modify-goal": ["3", "GoalId", "mathOp", "value32", ""],
    "up-object-data": ["3", "ObjectData", "compareOp", "value32", ""],
    "up-object-target-data": ["3", "ObjectData", "compareOp", "value32", ""],
    "up-object-type-count": ["4", "typeOp", "ObjectId", "compareOp", "value32"],
    "up-object-type-count-total": ["4", "typeOp", "ObjectId", "compareOp", "value32"],
    "up-path-distance": ["4", "Point", "Strict", "compareOp", "0|170"],
    "up-pending-objects": ["4", "typeOp", "ObjectId", "compareOp", "value32"],
    "up-pending-placement": ["2", "typeOp", "BuildingId", "", ""],
    "up-player-distance": ["3", "AnyPlayer", "compareOp", "0|170", ""],
    "up-players-in-game": ["3", "PlayerStance", "compareOp", "2", ""],
    "up-point-contains": ["3", "Point", "typeOp", "ObjectId", ""],
    "up-point-distance": ["4", "Point", "Point", "compareOp", "0|170"],
    "up-point-elevation": ["4", "Point", "compareOp", "value32", ""],
    "up-point-explored": ["3", "Point", "typeOp", "ExploredState", ""],
    "up-point-terrain": ["3", "Point", "compareOp", "Terrain", ""],
    "up-point-zone": ["3", "Point", "compareOp", "value32", ""],
    "up-projectile-detected": ["3", "ProjectileType", "compareOp", "ElapsedTime", ""],
    "up-projectile-target": ["3", "ProjectileType", "compareOp", "ClassId", ""],
    "up-remaining-boar-amount": ["2", "compareOp", "0|10", "", ""],
    "up-research-status": ["4", "typeOp", "TechId", "compareOp", "ResearchState"],
    "up-resource-amount": ["3", "ResourceAmount", "compareOp", "0|50000", ""],
    "up-resource-percent": ["3", "ResourceAmount", "compareOp", "0|100", ""],
    "up-set-target-by-id": ["2", "typeOp", "Id", "", ""],
    "up-set-target-object": ["3", "SearchSource", "typeOp", "0|239", ""],
    "up-timer-status": ["3", "TimerId", "compareOp", "TimerState", ""],
    "up-train-site-ready": ["2", "typeOp", "UnitIdStrict", "", ""],
    "up-unit-type-in-town": ["3", "typeOp", "UnitId", "compareOp", "0|200"],
    "up-villager-type-in-town": ["4", "typeOp", "83;293", "compareOp", "0|200"],
    "up-allied-resource-percent": [
        "4",
        "AllyPlayer",
        "ResourceAmount",
        "compareOp",
        "0|100",
    ],
    "up-find-local": ["4", "typeOp", "UnitId", "typeOp", "0|240"],
}

ACTIONS = {
    "acknowledge-event": ["2", "EventType", "EventID", "", ""],
    "attack-now": ["0", "", "", "", ""],
    "build": ["1", "Buildable", "", "", ""],
    "build-forward": ["1", "Buildable", "", "", ""],
    "build-gate": ["1", "Perimeter", "", "", ""],
    "build-wall": ["2", "Perimeter", "WallId", "", ""],
    "buy-commodity": ["1", "Commodity", "", "", ""],
    "clear-tribute-memory": ["2", "AnyPlayer", "Resource", "", ""],
    "delete-building": ["1", "BuildingId", "", "", ""],
    "delete-unit": ["1", "UnitIdStrict", "", "", ""],
    "disable-timer": ["1", "TimerId", "", "", ""],
    "disable-self": ["0", "", "", "", ""],
    "do-nothing": ["0", "", "", "", ""],
    "enable-timer": ["2", "TimerId", "value32Positive", "", ""],
    "enable-wall-placement": ["1", "Perimeter", "", "", ""],
    "generate-random-number": ["1", "value32Positive", "", "", ""],
    "release-escrow": ["1", "Resource", "", "", ""],
    "research": ["1", "TechId", "", "", ""],
    "sell-commodity": ["1", "Commodity", "", "", ""],
    "set-difficulty-parameter": ["2", "DiffParameterId", "0|100", "", ""],
    "set-doctrine": ["1", "value32", "", "", ""],
    "set-escrow-percentage": ["2", "Resource", "value32", "", ""],
    "set-goal": ["2", "GoalId", "value32", "", ""],
    "set-shared-goal": ["2", "SharedGoalId", "value32", "", ""],
    "set-signal": ["1", "SignalId", "", "", ""],
    "spy": ["0", "", "", "", ""],
    "train": ["1", "Trainable", "", "", ""],
    "tribute-to-player": ["3", "AnyPlayer", "Resource", "value32Positive", ""],
    "up-add-cost-data": ["3", "GoalId", "typeOp", "value32", ""],
    "up-add-object-by-id": ["3", "SearchSource", "typeOp", "Id", ""],
    "up-add-point": ["4", "Point", "Point", "typeOp", "value32"],
    "up-add-research-cost": ["4", "typeOp", "TechId", "typeOp", "value32"],
    "up-assign-builders": ["4", "typeOp", "Buildable", "typeOp", "-1|250"],
    "up-bound-point": ["2", "Point", "Point", "", ""],
    "up-bound-precise-point": ["4", "Point", "1", "typeOp", "value32Positive"],
    "up-build": ["4", "PlacementType", "EscrowState", "typeOp", "Buildable"],
    "up-build-line": ["4", "Point", "Point", "typeOp", "Buildable"],
    "up-buy-commodity": ["4", "typeOp", "ResourceAmount", "typeOp", "value32Positive"],
    "up-clean-search": ["3", "SearchSource", "ObjectData", "SearchOrder", ""],
    "up-copy-point": ["2", "Point", "Point", "", ""],
    "up-create-group": ["4", "GoalId", "GoalId2", "typeOp", "GroupId"],
    "up-cross-tiles": ["4", "Point", "Point", "typeOp", "value32"],
    "up-delete-distant-farms": ["2", "typeOp", "value256", "", ""],
    "up-delete-idle-units": ["1", "IdleType", "", "", ""],
    "up-delete-objects": ["4", "typeOp", "UnitIdStrict", "typeOp", "value32Positive"],
    "up-disband-group-type": ["1", "GroupType", "", "", ""],
    "up-drop-resources": ["3", "Resource", "typeOp", "value32Positive", ""],
    "up-garrison": ["3", "GarrisonableUnitId", "typeOp", "UnitId", ""],
    "up-gather-inside": ["4", "typeOp", "BuildingId", "typeOp", "State"],
    "up-get-attacker-class": ["1", "GoalId", "", "", ""],
    "up-get-cost-delta": ["1", "GoalId", "", "", ""],
    "up-get-event": ["3", "typeOp", "EventID", "GoalId", ""],
    "up-get-group-size": ["3", "typeOp", "GroupId", "GoalId", ""],
    "up-get-indirect-goal": ["3", "typeOp", "GoalId", "GoalId2", ""],
    "up-get-object-data": ["2", "ObjectData", "GoalId", "", ""],
    "up-get-object-target-data": ["2", "ObjectData", "GoalId", "", ""],
    "up-get-path-distance": ["3", "Point", "Strict", "GoalId", ""],
    "up-get-player-color": ["2", "AnyPlayer", "ColorId", "", ""],
    "up-get-point": ["2", "PositionType", "GoalId", "", ""],
    "up-get-point-contains": ["4", "GoalId", "GoalId2", "typeOp", "ObjectId"],
    "up-get-point-distance": ["3", "Point", "Point", "GoalId", ""],
    "up-get-point-elevation": ["2", "Point", "GoalId", "", ""],
    "up-get-point-terrain": ["2", "Point", "Terrain", "", ""],
    "up-get-point-zone": ["2", "Point", "GoalId", "", ""],
    "up-get-precise-time": ["2", "GoalId", "GoalId2", "", ""],
    "up-get-projectile-player": ["2", "ProjectileType", "PlayerId", "", ""],
    "up-get-rule-id": ["1", "RuleId", "", "", ""],
    "up-get-search-state": ["1", "GoalId", "", "", ""],
    "up-get-shared-goal": ["3", "typeOp", "SharedGoalId", "GoalId", ""],
    "up-get-signal": ["3", "typeOp", "SignalId", "GoalId", ""],
    "up-get-threat-data": ["4", "GoalId", "PlayerId", "GoalId", "GoalId2"],
    "up-get-timer": ["3", "typeOp", "TimerId", "GoalId", ""],
    "up-guard-unit": ["3", "ObjectId", "typeOp", "UnitId", ""],
    "up-jump-direct": ["2", "typeOp", "RuleId", "", ""],
    "up-jump-dynamic": ["2", "typeOp", "value32", "", ""],
    "up-jump-rule": ["1", "value32", "", "", ""],
    "up-lerp-percent": ["4", "Point", "Point", "typeOp", "value32"],
    "up-lerp-tiles": ["4", "Point", "Point", "typeOp", "value32"],
    "up-modify-escrow": ["3", "Resource", "mathOp", "value32", ""],
    "up-modify-goal": ["3", "GoalId", "mathOp", "value32", ""],
    "up-modify-group-flag": ["3", "OnOff", "typeOp", "GroupId", ""],
    "up-modify-sn": ["3", "SnId", "mathOp", "value32", ""],
    "up-release-escrow": ["0", "", "", "", ""],
    "up-remove-objects": ["4", "SearchSource", "ObjectData", "typeOp", "value32"],
    "up-request-hunters": ["2", "typeOp", "value32Positive", "", ""],
    "up-research": ["3", "EscrowState", "typeOp", "TechId", ""],
    "up-reset-attack-now": ["0", "", "", "", ""],
    "up-reset-building": ["3", "OnOff", "typeOp", "BuildingId", ""],
    "up-reset-cost-data": ["1", "GoalId", "", "", ""],
    "up-reset-filters": ["0", "", "", "", ""],
    "up-reset-group": ["2", "typeOp", "GroupId", "", ""],
    "up-reset-placement": ["2", "typeOp", "BuildingId", "", ""],
    "up-reset-search": ["4", "OnOff", "OnOff", "OnOff", "OnOff"],
    "up-reset-target-priorities": ["2", "OnOff", "OnOff", "", ""],
    "up-reset-unit": ["2", "typeOp", "UnitId", "", ""],
    "up-retask-gatherers": ["3", "Resource", "typeOp", "value32Positive", ""],
    "up-retreat-now": ["0", "", "", "", ""],
    "up-retreat-to": ["3", "ObjectId", "typeOp", "UnitId", ""],
    "up-sell-commodity": ["4", "typeOp", "ResourceAmount", "typeOp", "value32Positive"],
    "up-set-attack-stance": ["3", "UnitId", "typeOp", "AttackStance", ""],
    "up-set-defense-priority": ["4", "typeOp", "BuildingId", "typeOp", "value32"],
    "up-set-group": ["3", "SearchSource", "typeOp", "GroupId", ""],
    "up-set-indirect-goal": ["4", "typeOp", "GroupId", "typeOp", "value32"],
    "up-set-offense-priority": ["4", "typeOp", "ObjectId", "typeOp", "-1|11"],
    "up-set-placement-data": ["4", "AllyPlayer", "ObjectId", "typeOp", "-254|254"],
    "up-set-precise-target-point": ["1", "Point", "", "", ""],
    "up-set-shared-goal": ["4", "typeOp", "SharedGoalId", "typeOp", "value32"],
    "up-set-signal": ["4", "typeOp", "SignalId", "typeOp", "value32"],
    "up-set-target-by-id": ["2", "typeOp", "Id", "", ""],
    "up-set-target-object": ["3", "SearchSource", "typeOp", "0|239", ""],
    "up-set-target-point": ["1", "Point", "", "", ""],
    "up-set-timer": ["4", "typeOp", "TimerId", "typeOp", "value32Positive"],
    "up-setup-cost-data": ["2", "OnOff", "GoalId", "", ""],
    "up-store-map-name": ["1", "OnOff", "", "", ""],
    "up-store-object-name": ["0", "", "", "", ""],
    "up-store-player-name": ["1", "AnyPlayer", "", "", ""],
    "up-store-tech-name": ["1", "typeOp", "TechId", "", ""],
    "up-target-point": ["4", "Point", "TargetAction", "Formation", "AttackStance"],
    "up-train": ["3", "EscrowState", "typeOp", "Trainable", ""],
    "up-tribute-to-player": [
        "4",
        "AnyPlayer",
        "ResourceAmount",
        "typeOp",
        "value32Positive",
    ],
    "up-ungarrison": ["2", "typeOp", "ObjectId", "", ""],
    "up-update-targets": ["0", "", "", "", ""],
    "up-reset-scouts": ["0", "", "", "", ""],
    "set-strategic-number": ["2", "SnId", "SnValue", "", ""],
}

SN = {
    "272": "0|1",
    "225": "0|3",
    "258": "0|2",
    "41": "1|255",
    "98": "0|32767",
    "103": "0|1",
    "188": "0|1",
    "195": "-32768|32767",
    "135": "0|1",
    "136": "1|255",
    "295": "0|23",
    "255": "0|2",
    "86": "7|255",
    "4": "-1|32767",
    "3": "-1|32767",
    "5": "-1|32767",
    "76": "0|32767",
    "194": "0|1",
    "273": "0|1",
    "271": "0|1",
    "285": "0|1",
    "277": "0|15",
    "284": "0|1",
    "267": "0|1",
    "294": "0|1",
    "291": "0|3",
    "229": "0|1",
    "280": "-10000|10000",
    "278": "-1|1",
    "279": "-10000|10000",
    "281": "0|2",
    "248": "1|255",
    "219": "0|100",
    "218": "0|100",
    "244": "0|2",
    "242": "0|1",
    "254": "0|1",
    "247": "0|1",
    "264": "0|15",
    "20": "0|50",
    "276": "0|2",
    "251": "0|8",
    "163": "3|255",
    "117": "0|100",
    "156": "-100|100",
    "282": "0|3",
    "240": "0|1",
    "232": "0|1",
    "239": "0|1",
    "166": "3|255",
    "118": "0|100",
    "159": "-100|100",
    "75": "0|3",
    "230": "0|30",
    "131": "1|255",
    "256": "0|32767",
    "231": "0|1",
    "265": "0|1",
    "104": "0|32767",
    "134": "0|3",
    "167": "0|100",
    "287": "0|1",
    "263": "0|1",
    "286": "0|2",
    "260": "0|255",
    "149": "0|32767",
    "26": "0|32767",
    "60": "0|32767",
    "236": "-2|255",
    "234": "-2|255",
    "100": "0|32767",
    "274": "0|20",
    "237": "-2|255",
    "235": "-2|255",
    "238": "-2|255",
    "74": "0|255",
    "233": "-2|255",
    "87": "4|255",
    "216": "0|32767",
    "16": "0|32767",
    "204": "0|8",
    "252": "0|8",
    "59": "0|32767",
    "35": "0|32767",
    "245": "0|32767",
    "73": "0|255",
    "112": "10|32767",
    "261": "0|255",
    "36": "0|32767",
    "58": "0|32767",
    "61": "0|32767",
    "257": "0|200",
    "42": "0|32767",
    "226": "0|32767",
    "275": "0|40",
    "288": "0|40",
    "246": "0|32767",
    "228": "0|100",
    "227": "0|100",
    "243": "1|100",
    "1": "0|100",
    "0": "0|100",
    "2": "0|100",
    "19": "0|100",
    "179": "0|100",
    "269": "-10|10",
    "270": "0|1",
    "268": "0|255",
    "253": "0|2",
    "259": "0|255",
    "168": "0|32767",
    "148": "0|32767",
    "250": "1|255",
    "94": "0|32767",
    "93": "0|32767",
    "99": "0|32767",
    "109": "-32768|32767",
    "110": "-32768|32767",
    "111": "-32768|32767",
    "106": "-1|1",
    "107": "-1|32767",
    "108": "-1|1",
    "165": "3|255",
    "119": "0|100",
    "158": "-100|100",
    "249": "-1|8",
    "292": "0|6",
    "143": "0|1",
    "18": "-1|32767",
    "266": "0|899",
    "301": "-32768|32767",
    "293": "0|1",
    "203": "0|1",
    "262": "0|1",
    "283": "0|2",
    "164": "3|255",
    "120": "0|100",
    "157": "-100|100",
    "34": "0|255",
}

UNIT_BUILDING_MAP = {
    "archer-line": "archery-range",
    "cavalry-archer-line": "archery-range",
    "skirmisher-line": "archery-range",
    "militiaman-line": "barracks",
    "spearman-line": "barracks",
    "battering-ram-line": "siege-workshop",
    "mangonel-line": "siege-workshop",
    "scorpion-line": "siege-workshop",
    "knight-line": "stable",
    "scout-cavalry-line": "stable",
    "tarkan-line": "castle",
    "trebuchet": "castle",
    "monk": "monastery",
}

CLASS_LIST = [
    "-1",
    "900",
    "901",
    "902",
    "903",
    "904",
    "905",
    "906",
    "907",
    "908",
    "909",
    "910",
    "911",
    "912",
    "913",
    "914",
    "915",
    "918",
    "919",
    "920",
    "921",
    "922",
    "923",
    "927",
    "930",
    "932",
    "933",
    "935",
    "936",
    "939",
    "942",
    "943",
    "944",
    "947",
    "949",
    "951",
    "952",
    "954",
    "955",
    "958",
    "959",
]

BUILDABLE = PARAMETERS["Buildable"].split(";")

TRAINABLE = PARAMETERS["Trainable"].split(";")

FORMATIONS = ["-1", "2", "4", "7", "8"]

GOAL_FACTS = [
    "attack-soldier-count",
    "building-available",
    "building-count",
    "building-type-count",
    "can-afford-building",
    "can-afford-research",
    "can-afford-unit",
    "can-build",
    "can-buy-commodity",
    "can-research",
    "can-sell-commodity",
    "can-train",
    "civilian-population",
    "commodity-buying-price",
    "commodity-selling-price",
    "current-age",
    "current-age-time",
    "current-score",
    "defend-soldier-count",
    "doctrine",
    "dropsite-min-distance",
    "escrow-amount",
    "false",
    "food-amount",
    "game-time",
    "goal",
    "housing-headroom",
    "idle-farm-count",
    "military-population",
    "players-current-age",
    "players-current-age-time",
    "players-score",
    "population",
    "population-cap",
    "population-headroom",
    "random-number",
    "research-available",
    "research-completed",
    "resource-found",
    "shared-goal",
    "sheep-and-forage-too-far",
    "soldier-count",
    "stone-amount",
    "strategic-number",
    "town-under-attack",
    "true",
    "unit-available",
    "unit-count",
    "unit-count-total",
    "unit-type-count",
    "unit-type-count-total",
    "wood-amount",
    "up-can-build",
    "up-can-build-line",
    "up-can-research",
    "up-can-train",
    "up-defender-count",
    "up-enemy-buildings-in-town",
    "up-enemy-units-in-town",
    "up-enemy-villagers-in-town",
    "up-remaining-boar-amount",
    "up-research-status",
    "up-resource-amount",
    "up-resource-percent",
    "up-train-site-ready",
    "up-unit-type-in-town",
]

SIMPLE_COMPARE = [">", "<", "==", "!=", "<=", ">="]

PLAYER_LIST = CLASS_LIST + BUILDABLE + TRAINABLE

with open("resign.txt", "r", encoding="utf-8") as r:
    RESIGN_RULE = r.read()

if CONFIG.allow_towers:
    PARAMETERS["Buildable"] += ";watch-tower;guard-tower;keep"
