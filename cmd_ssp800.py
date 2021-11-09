req_cmd = {
    'main'  : 'Change main input number.',
    'minp+' : 'Steps to the next input.',
    'minp-' : 'Steps to the previous input.',
    'lspn'  : 'Sets the current configuration.',
    'vola'  : 'Sets the absolute volume, disables mute.',
    'mvol+' : 'Steps main volume up, disables mute.',
    'mvol-' : 'Steps main volume down, disables mute.',
    'mute'  : 'Enables mute.',
    'unmt'  : 'Disables mute.',
    'ball'  : 'Shift front balance 1 dB left.',
    'balc'  : 'Re-center front balance.',
    'balr'  : 'Shift front balance 1 dB right.',
    'sub+'  : '[Trim] adds 1dB to subwoofer.',
    'sub-'  : '[Trim] subtracts 1dB from subwoofer.',
    'sub2+' : '[Trim] adds 1dB to subwoofer 2.',
    'sub2-' : '[Trim] subtracts 1dB from subwoofer 2.',
    'sub3+' : '[Trim] adds 1dB to subwoofer 3.',
    'sub3-' : '[Trim] subtracts 1dB from subwoofer 3.',
    'cnt+'  : '[Trim] adds 1dB to center channel.',
    'cnt-'  : '[Trim] subtracts 1dB from center channel.',
    'srn+'  : '[Trim] adds 1dB to surround channel.',
    'srn-'  : '[Trim] subtracts 1dB from surround channel.',
    'bak+'  : '[Trim] adds 1dB to back channel.',
    'bak-'  : '[Trim] subtracts 1dB from back channel.',
    'trm0'  : '[Trim] resets all trim settings.',
    'lsy+'  : 'Adds 1ms to lip sync delay.',
    'lsy-'  : 'Subtracts 1ms from lip sync delay.',
    'lsy0'  : 'Resets lip sync delay.',
    'ddln'  : 'Enables dolby digital late night compression.',
    'ddnc'  : 'Disables dolby digital late night compression.',
    'stby'  : 'Puts preamp in standby (off) mode.',
    'oper'  : 'Puts preamp in operate (on) mode.',
    't1_0'  : 'Sets trigger 1 to 0 volts (off).',
    't1_1'  : 'Sets trigger 1 to 12 volts (on).',
    't2_0'  : 'Sets trigger 2 to 0 volts (off).',
    't2_1'  : 'Sets trigger 2 to 12 volts (on).',
    'lcd0'  : 'Sets LCD panel to screen saver mode.',
    'lcd1'  : 'Sets LCD panel to low.',
    'lcd2'  : 'Sets LCD panel to medium.',
    'lcd3'  : 'Sets LCD panel to high.',
    'irc'   : 'Pass IR remote code.',
    'csk'   : 'Set LCD and OSD skin color.',
    'eqon'  : 'Activates all defined room EQ filters.',
    'eqoff' : '[Trim] disable all defined room EQ filters.',
    'stat'  : 'Request device statistics.',
    'wait'  : 'Wait p1 milliseconds.'
}

req_p1 = {
    'stat' : {
        'main'  : 'Request main volume, mute, and input selection.',
        'auto'  : 'Quieries other than STAT will respond with info.',
        'off'   : 'Only STAT queries will respond with info.',
        'mode'  : 'Request current audio post-processing mode.',
        'audio' : 'Request audio signal and signal rate status',
        'video' : 'Request video signal status',
        'temp'  : 'Request operating temperature, in Celsius.',
        'vers'  : 'Request firmware and build information.',
        'ac'    : 'Request AC voltage sense information.',
    },
    'main' : {
        '1..20' : 'inputs',
    },
    'lspn' : {
        '1..6' : 'configurations',
    },
    'vola' : {
        '0..100' : 'absolute volume',
    },
    'wait' : {
        '1..5000' : 'milliseconds',
    },
    'csk' : {
        1 : 'blue',
        2 : 'blue2',  # seems to be the same as 1...
        3 : 'silver',
        4 : 'red',
        5 : 'green',
    },
    'irc' : {
        2 : 'input1',
        3 : 'input2',
        4 : 'input3',
        5 : 'input4',
        6 : 'input5',
        7 : 'input6',
        8 : 'input7',
        9 : 'input8',
        10 : 'input+',
        11 : 'input-',
        12 : 'standby',
        13 : 'mute',
        14 : 'info',
        15 : 'display',
        16 : 'volume+',
        17 : 'volume-',
        19 : 'night',
        21 : 'trim',
        56 : 'f1',
        57 : 'f2',
        68 : 'mode',
        84 : 'menu',
        85 : 'home',
        88 : 'up',
        89 : 'down',
        90 : 'left',
        91 : 'right',
        92 : 'enter',
        120 : 'input9',
        121 : 'input10',
        122 : 'input11',
        123 : 'input12',
        124 : 'input13',
        125 : 'input14',
        126 : 'input15',
        127 : 'input16',
        128 : 'input17',
        129 : 'input18',
        130 : 'input19',
        131 : 'input20',
        134 : 'f3',
        135 : 'f4',
        150 : 'standby_off',
        151 : 'standby_on',
        152 : 'mute_on',
        153 : 'mute_off',
        160 : 'night_on',
        161 : 'night_off',
        162 : 'trim_front',
        163 : 'trim_center',
        164 : 'trim_surround',
        165 : 'trim_sub',
        166 : 'trim_rear',
        167 : 'mode-',
        185 : 'config1',
        186 : 'config2',
        187 : 'config3',
        188 : 'config4',
        189 : 'config5',
        190 : 'config6',
        191 : 'preset_config',
        192 : 'profile',
        193 : 'mode0_mono',
        194 : 'mode1_stereo',
        195 : 'mode2_party',
        196 : 'mode3_mono_plus',
        197 : 'mode4_movie_plus',
        198 : 'mode5_music_plus',
        199 : 'mode6_dolby_pro_logic',
        200 : 'mode7_dolby_pliix_music',
        201 : 'mode8_dolby_pliix_movie',
        202 : 'mode9_dolby_pliix_matrix',
        203 : 'mode11_dts_neo6',
        204 : 'mode12_dts_neo6_cinema',
        205 : 'mode13_dts_neo6_music',
        206 : 'mode14_discrete',
        207 : 'mode15_dts_neo6_cinema_es',
        208 : 'mode16_dts_neo6_music_es',
        209 : 'mode17_dolby_digital_ex',
        210 : 'mode17_dolby_digital_ex_dup',
        211 : 'mode10_dolby_pliix_game',
        217 : 'lipsync',
        221 : 'trim_sub2',
        222 : 'trim_sub3',
        223 : 'sub0',
        224 : 'sub10-',
    },
}

rsp_count = {
    'stat' : {
        'main'  : 2,
        'mode'  : 1,
        'audio' : 1,
        'video' : 1,
        'temp'  : 1,
        'vers'  : 1,
        'ac'    : 1,
    },
}

rsp_p1 = {
    'audio' : {
        '0'  : 'reserved',
        '1'  : 'digital zero signal',
        '2'  : 'digital pcm',
        '3'  : 'dolby digital',
        '4'  : 'dts',
        '5'  : 'mpeg',
        '6'  : 'noise',
        '7'  : 'analog',
        '8'  : 'digital error',
        '9'  : 'dts es matrix',
        '10' : 'dts es discrete',
        '11' : 'dts 96 5.1',
        '12' : 'dts 96 matrix',
        '13' : 'dts 96 discrete',
        '14' : 'hdmi audio multi-channel',
        '15' : 'dts 96/24',
        '16' : 'digital pcm stereo',
        '17' : 'digital pcm multi-channel',
        '18' : 'digital pcm 96/24',
        '19' : 'aac',
        '20' : 'aac stereo',
        '21' : 'aac multi-channel',
        '22' : 'mp2',
        '23' : 'mp3',
        '24' : 'dolby digital plus',
        '25' : 'dolby true hd',
        '26' : 'dts master audio',
        '27' : 'dts high resolution',
        '28' : 'none',
        '29' : 'no signal',  # undocumented
    },
    'mode' : {
        '0'  : 'mono',
        '1'  : 'stereo',
        '2'  : 'party',
        '3'  : 'mono plus',
        '4'  : 'movie plus',
        '5'  : 'music plus',
        '6'  : 'dolby pro logic',
        '7'  : 'dolby pliix music',
        '8'  : 'dolby pliix movie',
        '9'  : 'dolby pliix matrix',
        '10' : 'dolby pliix game',
        '11' : 'dts neo6',
        '12' : 'dts neo6 cinema',
        '13' : 'dts neo6 music',
        '14' : 'discrete',
        '15' : 'dts neo6 cinema es',
        '16' : 'dts neo6 music es',
        '17' : 'dolby digital ex',
        '18' : 'undocumented',
    },
    'video' : {
        '0'  : 'no signal',
        '1'  : '480i 4:3',
        '2'  : '576i 4:3',
        '3'  : '480p 4:3',
        '4'  : '576p 4:3',
        '5'  : '480i 16:9',
        '6'  : '576i 16:9',
        '7'  : '480p 16:9',
        '8'  : '576p 16:9',
        '9'  : '720p 60Hz',
        '10' : '720p 50Hz',
        '11' : '768p 60Hz',
        '12' : '1080i 60Hz',
        '13' : '1080i 50Hz',
        '14' : '1080p 60Hz',
        '15' : '1080p 50Hz',
        '16' : '1080p 24Hz',
        '17' : 'unsupported',
        '18' : 'vga',
    },

}

rsp_p2 = {
    'audio' : {
        '2'  : '32 kHz',
        '3'  : '44.1 kHz',
        '4'  : '48 kHz',
        '5'  : '88.2 kHz',
        '6'  : '96 kHz',
        '7'  : '192 kHz',
        '10' : '176 kHz',
    },
}

def is_int(s):
    if isinstance(s, int):
        return True
    if isinstance(s, str) and s:
        if s[0] in ('-', '+'):
            s = s[1:]
        return s.isdigit()
    return False


def in_range(n, _range):
    if isinstance(_range, str) and '..' in _range:
        lo, _, hi = _range.partition('..')
        return int(lo) <= n <= int(hi)
    return False


def req_p1_convert(c, r, p1):
    p1_int = is_int(p1)
    if p1_int:
        p1 = int(p1)
    for k in r:
        k_str = isinstance(k, str)
        if p1_int:
            if k_str:
                if in_range(p1, k):
                    return True, p1
            elif p1 == k:
                return True, p1
        else:
            if k_str:
                if p1 == k:
                    return True, p1
            elif p1 == r[k]:
                return True, k
    return False, p1


def request(c):
    c = c.lower()
    if not c or not isinstance(c, str):
        return False, f"ERR invalid cmd '{c}'"
    sp = c.split()
    sp_len = len(sp)
    if sp_len > 2:
        return False, f"ERR invalid extra cmd parms '{c}'"
    name = sp[0]
    if name not in req_cmd:
        return False, f"ERR invalid cmd name '{name}'"
    r = req_p1.get(name, None)
    if r is None:
        if sp_len > 1:
            return False, f"ERR cmd does not accept parms '{c}'"
    else:
        if sp_len < 2:
            return False, f"ERR parm required for '{name}'"
        ok, p1 = req_p1_convert(c, r, sp[1])
        if not ok:
            return False, f"ERR cmd invalid parm {c}"
        c = f"{name} {p1}"
    return True, c


def response(c):
    if c.startswith('SY'):
        sp = c.split()
        if len(sp) < 2:
            return False, f"ERR malformed response '{c}'"
        name = sp[1].lower()
        if name in rsp_p1:
            p1 = sp[2]
            val = rsp_p1[name].get(p1, p1)
            if val != p1:
                val = f"{val} ({p1})"
            if name in rsp_p2:
                p2 = sp[3]
                val2 = rsp_p2[name].get(p2, p2)
                if val2 != p2:
                    val2 = f"{val2} ({p2})"
                val = f"{val} @ {val2}"
            c = f"{sp[0]} {sp[1]} {val}"
    return True, c


def commands():
    a = []
    for name in req_cmd:
        a.append({ 'name' : name,
                   'desc' : req_cmd[name],
                   'p1'   : req_p1.get(name, {}) })
    return a
