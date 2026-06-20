#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["hidapi>=0.14"]
# ///


import argparse
import json
import sys
import time
import hid

# ========================================================================
# VIA v2 keycode tables — generated verbatim from the-via/app
# src/utils/key-to-byte/default.ts + deprecated-keycodes.ts (protocol v9).
# ========================================================================
BASIC_KEY_TO_BYTE = {
    '_QK_MODS': 0x0100,
    '_QK_MODS_MAX': 0x1fff,
    '_QK_MOD_TAP': 0x6000,
    '_QK_MOD_TAP_MAX': 0x7fff,
    '_QK_LAYER_TAP': 0x4000,
    '_QK_LAYER_TAP_MAX': 0x4fff,
    '_QK_LAYER_MOD': 0x5900,
    '_QK_LAYER_MOD_MAX': 0x59ff,
    '_QK_TO': 0x5010,
    '_QK_TO_MAX': 0x501f,
    '_QK_MOMENTARY': 0x5100,
    '_QK_MOMENTARY_MAX': 0x511f,
    '_QK_DEF_LAYER': 0x5200,
    '_QK_DEF_LAYER_MAX': 0x521f,
    '_QK_TOGGLE_LAYER': 0x5300,
    '_QK_TOGGLE_LAYER_MAX': 0x531f,
    '_QK_ONE_SHOT_LAYER': 0x5400,
    '_QK_ONE_SHOT_LAYER_MAX': 0x541f,
    '_QK_ONE_SHOT_MOD': 0x5500,
    '_QK_ONE_SHOT_MOD_MAX': 0x55ff,
    '_QK_LAYER_TAP_TOGGLE': 0x5800,
    '_QK_LAYER_TAP_TOGGLE_MAX': 0x581f,
    '_QK_LAYER_MOD_MASK': 0x000f,
    '_QK_MACRO': 0x5f12,
    '_QK_MACRO_MAX': 0x5f21,
    '_QK_KB': 0x5f80,
    '_QK_KB_MAX': 0x5f8f,
    'KC_NO': 0x0000,
    'KC_TRNS': 0x0001,
    'KC_A': 0x0004,
    'KC_B': 0x0005,
    'KC_C': 0x0006,
    'KC_D': 0x0007,
    'KC_E': 0x0008,
    'KC_F': 0x0009,
    'KC_G': 0x000a,
    'KC_H': 0x000b,
    'KC_I': 0x000c,
    'KC_J': 0x000d,
    'KC_K': 0x000e,
    'KC_L': 0x000f,
    'KC_M': 0x0010,
    'KC_N': 0x0011,
    'KC_O': 0x0012,
    'KC_P': 0x0013,
    'KC_Q': 0x0014,
    'KC_R': 0x0015,
    'KC_S': 0x0016,
    'KC_T': 0x0017,
    'KC_U': 0x0018,
    'KC_V': 0x0019,
    'KC_W': 0x001a,
    'KC_X': 0x001b,
    'KC_Y': 0x001c,
    'KC_Z': 0x001d,
    'KC_1': 0x001e,
    'KC_2': 0x001f,
    'KC_3': 0x0020,
    'KC_4': 0x0021,
    'KC_5': 0x0022,
    'KC_6': 0x0023,
    'KC_7': 0x0024,
    'KC_8': 0x0025,
    'KC_9': 0x0026,
    'KC_0': 0x0027,
    'KC_ENT': 0x0028,
    'KC_ESC': 0x0029,
    'KC_BSPC': 0x002a,
    'KC_TAB': 0x002b,
    'KC_SPC': 0x002c,
    'KC_MINS': 0x002d,
    'KC_EQL': 0x002e,
    'KC_LBRC': 0x002f,
    'KC_RBRC': 0x0030,
    'KC_BSLS': 0x0031,
    'KC_NUHS': 0x0032,
    'KC_SCLN': 0x0033,
    'KC_QUOT': 0x0034,
    'KC_GRV': 0x0035,
    'KC_COMM': 0x0036,
    'KC_DOT': 0x0037,
    'KC_SLSH': 0x0038,
    'KC_CAPS': 0x0039,
    'KC_F1': 0x003a,
    'KC_F2': 0x003b,
    'KC_F3': 0x003c,
    'KC_F4': 0x003d,
    'KC_F5': 0x003e,
    'KC_F6': 0x003f,
    'KC_F7': 0x0040,
    'KC_F8': 0x0041,
    'KC_F9': 0x0042,
    'KC_F10': 0x0043,
    'KC_F11': 0x0044,
    'KC_F12': 0x0045,
    'KC_PSCR': 0x0046,
    'KC_SLCK': 0x0047,
    'KC_PAUS': 0x0048,
    'KC_INS': 0x0049,
    'KC_HOME': 0x004a,
    'KC_PGUP': 0x004b,
    'KC_DEL': 0x004c,
    'KC_END': 0x004d,
    'KC_PGDN': 0x004e,
    'KC_RGHT': 0x004f,
    'KC_LEFT': 0x0050,
    'KC_DOWN': 0x0051,
    'KC_UP': 0x0052,
    'KC_NLCK': 0x0053,
    'KC_PSLS': 0x0054,
    'KC_PAST': 0x0055,
    'KC_PMNS': 0x0056,
    'KC_PPLS': 0x0057,
    'KC_PENT': 0x0058,
    'KC_P1': 0x0059,
    'KC_P2': 0x005a,
    'KC_P3': 0x005b,
    'KC_P4': 0x005c,
    'KC_P5': 0x005d,
    'KC_P6': 0x005e,
    'KC_P7': 0x005f,
    'KC_P8': 0x0060,
    'KC_P9': 0x0061,
    'KC_P0': 0x0062,
    'KC_PDOT': 0x0063,
    'KC_NUBS': 0x0064,
    'KC_APP': 0x0065,
    'KC_POWER': 0x0066,
    'KC_PEQL': 0x0067,
    'KC_F13': 0x0068,
    'KC_F14': 0x0069,
    'KC_F15': 0x006a,
    'KC_F16': 0x006b,
    'KC_F17': 0x006c,
    'KC_F18': 0x006d,
    'KC_F19': 0x006e,
    'KC_F20': 0x006f,
    'KC_F21': 0x0070,
    'KC_F22': 0x0071,
    'KC_F23': 0x0072,
    'KC_F24': 0x0073,
    'KC_EXECUTE': 0x0074,
    'KC_HELP': 0x0075,
    'KC_MENU': 0x0076,
    'KC_SELECT': 0x0077,
    'KC_STOP': 0x0078,
    'KC_AGAIN': 0x0079,
    'KC_UNDO': 0x007a,
    'KC_CUT': 0x007b,
    'KC_COPY': 0x007c,
    'KC_PASTE': 0x007d,
    'KC_FIND': 0x007e,
    'KC_LCAP': 0x0082,
    'KC_LNUM': 0x0083,
    'KC_LSCR': 0x0084,
    'KC_PCMM': 0x0085,
    'KC_KP_EQUAL_AS400': 0x0086,
    'KC_RO': 0x0087,
    'KC_KANA': 0x0088,
    'KC_JYEN': 0x0089,
    'KC_HENK': 0x008a,
    'KC_MHEN': 0x008b,
    'KC_INT6': 0x008c,
    'KC_INT7': 0x008d,
    'KC_INT8': 0x008e,
    'KC_INT9': 0x008f,
    'KC_HAEN': 0x0090,
    'KC_HANJ': 0x0091,
    'KC_LANG3': 0x0092,
    'KC_LANG4': 0x0093,
    'KC_LANG5': 0x0094,
    'KC_LANG6': 0x0095,
    'KC_LANG7': 0x0096,
    'KC_LANG8': 0x0097,
    'KC_LANG9': 0x0098,
    'KC_ERAS': 0x0099,
    'KC_SYSREQ': 0x009a,
    'KC_CANCEL': 0x009b,
    'KC_CLR': 0x009c,
    'KC_CLEAR': 0x009c,
    'KC_PRIOR': 0x009d,
    'KC_OUT': 0x00a0,
    'KC_OPER': 0x00a1,
    'KC_CLEAR_AGAIN': 0x00a2,
    'KC_CRSEL': 0x00a3,
    'KC_EXSEL': 0x00a4,
    'KC_PWR': 0x00a5,
    'KC_SLEP': 0x00a6,
    'KC_WAKE': 0x00a7,
    'KC_MUTE': 0x00a8,
    'KC_VOLU': 0x00a9,
    'KC_VOLD': 0x00aa,
    'KC_MNXT': 0x00ab,
    'KC_MPRV': 0x00ac,
    'KC_MSTP': 0x00ad,
    'KC_MPLY': 0x00ae,
    'KC_MSEL': 0x00af,
    'KC_EJCT': 0x00b0,
    'KC_MAIL': 0x00b1,
    'KC_CALC': 0x00b2,
    'KC_MYCM': 0x00b3,
    'KC_WWW_SEARCH': 0x00b4,
    'KC_WWW_HOME': 0x00b5,
    'KC_WWW_BACK': 0x00b6,
    'KC_WWW_FORWARD': 0x00b7,
    'KC_WWW_STOP': 0x00b8,
    'KC_WWW_REFRESH': 0x00b9,
    'KC_WWW_FAVORITES': 0x00ba,
    'KC_MFFD': 0x00bb,
    'KC_MRWD': 0x00bc,
    'KC_BRIU': 0x00bd,
    'KC_BRID': 0x00be,
    'KC_MCTL': 0x00c1,
    'KC_LPAD': 0x00c2,
    'KC_LCTL': 0x00e0,
    'KC_LSFT': 0x00e1,
    'KC_LALT': 0x00e2,
    'KC_LGUI': 0x00e3,
    'KC_RCTL': 0x00e4,
    'KC_RSFT': 0x00e5,
    'KC_RALT': 0x00e6,
    'KC_RGUI': 0x00e7,
    'KC_MS_UP': 0x00f0,
    'KC_MS_DOWN': 0x00f1,
    'KC_MS_LEFT': 0x00f2,
    'KC_MS_RIGHT': 0x00f3,
    'KC_MS_BTN1': 0x00f4,
    'KC_MS_BTN2': 0x00f5,
    'KC_MS_BTN3': 0x00f6,
    'KC_MS_BTN4': 0x00f7,
    'KC_MS_BTN5': 0x00f8,
    'KC_MS_WH_UP': 0x00f9,
    'KC_MS_WH_DOWN': 0x00fa,
    'KC_MS_WH_LEFT': 0x00fb,
    'KC_MS_WH_RIGHT': 0x00fc,
    'KC_MS_ACCEL0': 0x00fd,
    'KC_MS_ACCEL1': 0x00fe,
    'KC_MS_ACCEL2': 0x00ff,
    'RESET': 0x5c00,
    'DEBUG': 0x5c01,
    'MAGIC_TOGGLE_NKRO': 0x5c14,
    'KC_GESC': 0x5c16,
    'AU_ON': 0x5c1d,
    'AU_OFF': 0x5c1e,
    'AU_TOG': 0x5c1f,
    'CLICKY_TOGGLE': 0x5c20,
    'CLICKY_ENABLE': 0x5c21,
    'CLICKY_DISABLE': 0x5c22,
    'CLICKY_UP': 0x5c23,
    'CLICKY_DOWN': 0x5c24,
    'CLICKY_RESET': 0x5c25,
    'MU_ON': 0x5c26,
    'MU_OFF': 0x5c27,
    'MU_TOG': 0x5c28,
    'MU_MOD': 0x5c29,
    'BL_ON': 0x5cbb,
    'BL_OFF': 0x5cbc,
    'BL_DEC': 0x5cbd,
    'BL_INC': 0x5cbe,
    'BL_TOGG': 0x5cbf,
    'BL_STEP': 0x5cc0,
    'BL_BRTG': 0x5cc1,
    'RGB_TOG': 0x5cc2,
    'RGB_MOD': 0x5cc3,
    'RGB_RMOD': 0x5cc4,
    'RGB_HUI': 0x5cc5,
    'RGB_HUD': 0x5cc6,
    'RGB_SAI': 0x5cc7,
    'RGB_SAD': 0x5cc8,
    'RGB_VAI': 0x5cc9,
    'RGB_VAD': 0x5cca,
    'RGB_SPI': 0x5ccb,
    'RGB_SPD': 0x5ccc,
    'RGB_M_P': 0x5ccd,
    'RGB_M_B': 0x5cce,
    'RGB_M_R': 0x5ccf,
    'RGB_M_SW': 0x5cd0,
    'RGB_M_SN': 0x5cd1,
    'RGB_M_K': 0x5cd2,
    'RGB_M_X': 0x5cd3,
    'RGB_M_G': 0x5cd4,
    'KC_LSPO': 0x5cd7,
    'KC_RSPC': 0x5cd8,
    'KC_SFTENT': 0x5cd9,
    'KC_LCPO': 0x5cf3,
    'KC_RCPC': 0x5cf4,
    'KC_LAPO': 0x5cf5,
    'KC_RAPC': 0x5cf6,
    'BR_INC': 0x5f00,
    'BR_DEC': 0x5f01,
    'EF_INC': 0x5f02,
    'EF_DEC': 0x5f03,
    'ES_INC': 0x5f04,
    'ES_DEC': 0x5f05,
    'H1_INC': 0x5f06,
    'H1_DEC': 0x5f07,
    'S1_INC': 0x5f08,
    'S1_DEC': 0x5f09,
    'H2_INC': 0x5f0a,
    'H2_DEC': 0x5f0b,
    'S2_INC': 0x5f0c,
    'S2_DEC': 0x5f0d,
    'FN_MO13': 0x5f10,
    'FN_MO23': 0x5f11,
}

# Deprecated/alias keycode names -> canonical code string
ALIASES = {
    'KC_TILD': 'S(KC_GRV)',
    'KC_EXLM': 'S(KC_1)',
    'KC_AT': 'S(KC_2)',
    'KC_HASH': 'S(KC_3)',
    'KC_DLR': 'S(KC_4)',
    'KC_PERC': 'S(KC_5)',
    'KC_CIRC': 'S(KC_6)',
    'KC_AMPR': 'S(KC_7)',
    'KC_ASTR': 'S(KC_8)',
    'KC_LPRN': 'S(KC_9)',
    'KC_RPRN': 'S(KC_0)',
    'KC_UNDS': 'S(KC_MINS)',
    'KC_PLUS': 'S(KC_EQL)',
    'KC_LCBR': 'S(KC_LBRC)',
    'KC_RCBR': 'S(KC_RBRC)',
    'KC_PIPE': 'S(KC_BSLS)',
    'KC_COLN': 'S(KC_SCLN)',
    'KC_DQUO': 'S(KC_QUOT)',
    'KC_LT': 'S(KC_COMM)',
    'KC_GT': 'S(KC_DOT)',
    'KC_QUES': 'S(KC_SLSH)',
    'SPC_FN1': 'LT(1,KC_SPC)',
    'SPC_FN2': 'LT(2,KC_SPC)',
    'SPC_FN3': 'LT(3,KC_SPC)',
    'MACRO00': 'MACRO(0)',
    'MACRO01': 'MACRO(1)',
    'MACRO02': 'MACRO(2)',
    'MACRO03': 'MACRO(3)',
    'MACRO04': 'MACRO(4)',
    'MACRO05': 'MACRO(5)',
    'MACRO06': 'MACRO(6)',
    'MACRO07': 'MACRO(7)',
    'MACRO08': 'MACRO(8)',
    'MACRO09': 'MACRO(9)',
    'MACRO10': 'MACRO(10)',
    'MACRO11': 'MACRO(11)',
    'MACRO12': 'MACRO(12)',
    'MACRO13': 'MACRO(13)',
    'MACRO14': 'MACRO(14)',
    'MACRO15': 'MACRO(15)',
    'USER00': 'CUSTOM(0)',
    'USER01': 'CUSTOM(1)',
    'USER02': 'CUSTOM(2)',
    'USER03': 'CUSTOM(3)',
    'USER04': 'CUSTOM(4)',
    'USER05': 'CUSTOM(5)',
    'USER06': 'CUSTOM(6)',
    'USER07': 'CUSTOM(7)',
    'USER08': 'CUSTOM(8)',
    'USER09': 'CUSTOM(9)',
    'USER10': 'CUSTOM(10)',
    'USER11': 'CUSTOM(11)',
    'USER12': 'CUSTOM(12)',
    'USER13': 'CUSTOM(13)',
    'USER14': 'CUSTOM(14)',
    'USER15': 'CUSTOM(15)',
}

# ========================================================================
# Keycode <-> byte conversion — faithful port of VIA key.ts / advanced-keys.ts
# ========================================================================
import re
B = BASIC_KEY_TO_BYTE  # short alias used throughout this section

# ---- quantum ranges (from advanced-keys.ts topLevelMacroToValue) ----
_RANGE = {
    'MT':  '_QK_MOD_TAP',
    'LT':  '_QK_LAYER_TAP',
    'LM':  '_QK_LAYER_MOD',
    'TO':  '_QK_TO',
    'MO':  '_QK_MOMENTARY',
    'DF':  '_QK_DEF_LAYER',
    'TG':  '_QK_TOGGLE_LAYER',
    'OSL': '_QK_ONE_SHOT_LAYER',
    'OSM': '_QK_ONE_SHOT_MOD',
    'TT':  '_QK_LAYER_TAP_TOGGLE',
    'CUSTOM': '_QK_KB',
    'MACRO':  '_QK_MACRO',
}

_MOD_CODES = {
    'QK_LCTL': 0x0100, 'QK_LSFT': 0x0200, 'QK_LALT': 0x0400, 'QK_LGUI': 0x0800,
    'QK_RMODS_MIN': 0x1000,
    'QK_RCTL': 0x1100, 'QK_RSFT': 0x1200, 'QK_RALT': 0x1400, 'QK_RGUI': 0x1800,
}
_MOD_KEY_TO_VALUE = {
    'LCTL': _MOD_CODES['QK_LCTL'], 'C': _MOD_CODES['QK_LCTL'],
    'LSFT': _MOD_CODES['QK_LSFT'], 'S': _MOD_CODES['QK_LSFT'],
    'LALT': _MOD_CODES['QK_LALT'], 'A': _MOD_CODES['QK_LALT'],
    'LGUI': _MOD_CODES['QK_LGUI'], 'LCMD': _MOD_CODES['QK_LGUI'],
    'LWIN': _MOD_CODES['QK_LGUI'], 'G': _MOD_CODES['QK_LGUI'],
    'RCTL': _MOD_CODES['QK_RCTL'], 'RSFT': _MOD_CODES['QK_RSFT'],
    'ALGR': _MOD_CODES['QK_RALT'], 'RALT': _MOD_CODES['QK_RALT'],
    'RCMD': _MOD_CODES['QK_RGUI'], 'RWIN': _MOD_CODES['QK_RGUI'],
    'RGUI': _MOD_CODES['QK_RGUI'],
    'SCMD': _MOD_CODES['QK_LSFT'] | _MOD_CODES['QK_LGUI'],
    'SWIN': _MOD_CODES['QK_LSFT'] | _MOD_CODES['QK_LGUI'],
    'SGUI': _MOD_CODES['QK_LSFT'] | _MOD_CODES['QK_LGUI'],
    'LSG':  _MOD_CODES['QK_LSFT'] | _MOD_CODES['QK_LGUI'],
    'LAG':  _MOD_CODES['QK_LALT'] | _MOD_CODES['QK_LGUI'],
    'RSG':  _MOD_CODES['QK_RSFT'] | _MOD_CODES['QK_RGUI'],
    'RAG':  _MOD_CODES['QK_RALT'] | _MOD_CODES['QK_RGUI'],
    'LCA':  _MOD_CODES['QK_LCTL'] | _MOD_CODES['QK_LALT'],
    'LSA':  _MOD_CODES['QK_LSFT'] | _MOD_CODES['QK_LALT'],
    'SAGR': _MOD_CODES['QK_RSFT'] | _MOD_CODES['QK_RALT'],
    'RSA':  _MOD_CODES['QK_RSFT'] | _MOD_CODES['QK_RALT'],
    'RCS':  _MOD_CODES['QK_RCTL'] | _MOD_CODES['QK_RSFT'],
    'LCAG': _MOD_CODES['QK_LCTL'] | _MOD_CODES['QK_LALT'] | _MOD_CODES['QK_LGUI'],
    'MEH':  _MOD_CODES['QK_LCTL'] | _MOD_CODES['QK_LALT'] | _MOD_CODES['QK_LSFT'],
    'HYPR': _MOD_CODES['QK_LCTL'] | _MOD_CODES['QK_LALT'] | _MOD_CODES['QK_LSFT'] | _MOD_CODES['QK_LGUI'],
}
_MOD_MASKS = {
    'MOD_LCTL': 0x0001, 'MOD_LSFT': 0x0002, 'MOD_LALT': 0x0004, 'MOD_LGUI': 0x0008,
    'MOD_RCTL': 0x0011, 'MOD_RSFT': 0x0012, 'MOD_RALT': 0x0014, 'MOD_RGUI': 0x0018,
    'MOD_HYPR': 0x000f, 'MOD_MEH': 0x0007,
}

# layer codes handled by getByteForLayerCode in key.ts: NAME(number)
_LAYER_CODE_RE = re.compile(r'^([A-Za-z]+)\((\d+)\)$')
# generic NAME(args) for advanced
_TOPLEVEL_RE = re.compile(r'^([A-Za-z_]+)\((.*)\)$')


class KeycodeError(ValueError):
    pass


# ---------------------------------------------------------------- name -> byte
def _parse_mods(s):
    parts = [p.strip() for p in s.split('|')]
    val = 0
    for p in parts:
        if p not in _MOD_MASKS:
            return 0
        val |= _MOD_MASKS[p]
    return val


def _advanced_string_to_keycode(code):
    """Port of advancedStringToKeycode + parseTopLevelMacro/parseModifierCode."""
    upper = code.upper()
    parts = [p.strip() for p in re.split(r'[()]', upper)]
    head = parts[0]
    if head in _RANGE:
        return _parse_top_level_macro(head, parts[1] if len(parts) > 1 else '')
    if head in _MOD_KEY_TO_VALUE:
        return _parse_modifier_code(parts)
    return 0


def _parse_top_level_macro(key, parameter):
    if key in ('MO', 'DF', 'TG', 'OSL', 'TT', 'TO'):
        layer = int(parameter)
        if layer < 0:
            return 0
        return B[_RANGE[key]] | (layer & 0xff)
    if key == 'OSM':
        mods = _parse_mods(parameter)
        return 0 if mods == 0 else B[_RANGE[key]] | (mods & 0xff)
    if key == 'LM':
        p1, p2 = [s.strip() for s in parameter.split(',')]
        mask = B['_QK_LAYER_MOD_MASK']; shift = (mask + 1).bit_length() - 1
        layer = int(p1); mods = _parse_mods(p2)
        if layer < 0 or mods == 0:
            return 0
        return B[_RANGE[key]] | ((layer & 0xf) << shift) | (mods & mask)
    if key == 'LT':
        p1, p2 = [s.strip() for s in parameter.split(',')]
        layer = int(p1)
        if layer < 0 or p2 not in B:
            return 0
        return B[_RANGE[key]] | ((layer & 0xf) << 8) | B[p2]
    if key == 'MT':
        p1, p2 = [s.strip() for s in parameter.split(',')]
        mods = _parse_mods(p1)
        if mods == 0 or p2 not in B:
            return 0
        return B[_RANGE[key]] | ((mods & 0x1f) << 8) | (B[p2] & 0xff)
    if key == 'CUSTOM':
        n = int(parameter); nmax = B['_QK_KB_MAX'] - B['_QK_KB']
        return B[_RANGE[key]] + n if 0 <= n <= nmax else 0
    if key == 'MACRO':
        n = int(parameter); nmax = B['_QK_MACRO_MAX'] - B['_QK_MACRO']
        return B[_RANGE[key]] + n if 0 <= n <= nmax else 0
    return 0


def _parse_modifier_code(parts):
    real = [p for p in parts if p]
    out = 0
    for idx, part in enumerate(real):
        if idx == len(real) - 1:           # last must be a KC code
            if part not in B:
                return 0
            out |= B[part]
        else:                              # leading parts are modifiers
            if part not in _MOD_KEY_TO_VALUE:
                return 0
            out |= _MOD_KEY_TO_VALUE[part]
    return out


def code_to_byte(code):
    """VIA getByteForCode. Accepts KC_* names, aliases, NAME(n) layer/custom/macro
    codes, modifier/LT/MT codes, and raw hex strings like '0x5f93'."""
    code = code.strip()
    if code in ALIASES:
        code = ALIASES[code]
    if code in B:
        return B[code]
    # raw hex passthrough (VIA emits these for keyboard-specific codes)
    if re.fullmatch(r'0x[0-9a-fA-F]+', code):
        return int(code, 16)
    # layer code NAME(number)
    m = _LAYER_CODE_RE.match(code)
    if m:
        b = _byte_for_layer_code(m.group(1), int(m.group(2)))
        if b is not None:
            return b
    adv = _advanced_string_to_keycode(code)
    if adv:
        return adv
    raise KeycodeError(f"Could not find byte for {code!r}")


def _byte_for_layer_code(name, n):
    table = {
        'TO':  ('_QK_TO', '_QK_TO_MAX'),
        'MO':  ('_QK_MOMENTARY', '_QK_MOMENTARY_MAX'),
        'DF':  ('_QK_DEF_LAYER', '_QK_DEF_LAYER_MAX'),
        'TG':  ('_QK_TOGGLE_LAYER', '_QK_TOGGLE_LAYER_MAX'),
        'OSL': ('_QK_ONE_SHOT_LAYER', '_QK_ONE_SHOT_LAYER_MAX'),
        'TT':  ('_QK_LAYER_TAP_TOGGLE', '_QK_LAYER_TAP_TOGGLE_MAX'),
        'CUSTOM': ('_QK_KB', '_QK_KB_MAX'),
        'MACRO':  ('_QK_MACRO', '_QK_MACRO_MAX'),
    }
    if name not in table:
        return None
    base, mx = table[name]
    return min(B[base] + n, B[mx])


# ---------------------------------------------------------------- byte -> name
_BYTE_TO_KEY = {}
for _name, _val in B.items():
    # mirror VIA getByteToKey: prefer a real (non _QK) name when several map to one byte
    if _val in _BYTE_TO_KEY:
        if _name.startswith('_QK'):
            continue
        if _BYTE_TO_KEY[_val].startswith('_QK'):
            _BYTE_TO_KEY[_val] = _name
    else:
        _BYTE_TO_KEY[_val] = _name

_QUANTUM_PAIRS = [
    ('_QK_TO', '_QK_TO_MAX'),
    ('_QK_MOMENTARY', '_QK_MOMENTARY_MAX'),
    ('_QK_DEF_LAYER', '_QK_DEF_LAYER_MAX'),
    ('_QK_TOGGLE_LAYER', '_QK_TOGGLE_LAYER_MAX'),
    ('_QK_ONE_SHOT_LAYER', '_QK_ONE_SHOT_LAYER_MAX'),
    ('_QK_LAYER_TAP_TOGGLE', '_QK_LAYER_TAP_TOGGLE_MAX'),
    ('_QK_KB', '_QK_KB_MAX'),
    ('_QK_MACRO', '_QK_MACRO_MAX'),
]


def _is_layer_key(byte):
    return any(B[a] <= byte <= B[b] for a, b in _QUANTUM_PAIRS)


def _code_for_layer_byte(byte):
    for name, (base, mx) in {
        'TO': ('_QK_TO', '_QK_TO_MAX'),
        'MO': ('_QK_MOMENTARY', '_QK_MOMENTARY_MAX'),
        'DF': ('_QK_DEF_LAYER', '_QK_DEF_LAYER_MAX'),
        'TG': ('_QK_TOGGLE_LAYER', '_QK_TOGGLE_LAYER_MAX'),
        'OSL': ('_QK_ONE_SHOT_LAYER', '_QK_ONE_SHOT_LAYER_MAX'),
        'TT': ('_QK_LAYER_TAP_TOGGLE', '_QK_LAYER_TAP_TOGGLE_MAX'),
        'CUSTOM': ('_QK_KB', '_QK_KB_MAX'),
        'MACRO': ('_QK_MACRO', '_QK_MACRO_MAX'),
    }.items():
        if B[base] <= byte <= B[mx]:
            return f"{name}({byte - B[base]})"
    return None


_MOD_VALUE_TO_KEY = {v: k for k, v in _MOD_KEY_TO_VALUE.items()}
_LEFT_MOD_V2K = {v: k for k, v in _MOD_KEY_TO_VALUE.items()
                 if v in _MOD_CODES.values() and v < _MOD_CODES['QK_RMODS_MIN']}
_RIGHT_MOD_V2K = {v: k for k, v in _MOD_KEY_TO_VALUE.items()
                  if v in _MOD_CODES.values() and v >= _MOD_CODES['QK_RMODS_MIN']}


def _mod_value_to_string(mask):
    out = []
    for name, bit in _MOD_MASKS.items():
        if name in ('MOD_HYPR', 'MOD_MEH'):
            continue
        if (bit & mask) == bit:
            out.append(name)
    return ' | '.join(out)


def _top_level_mod_to_string(keycode):
    contained = _BYTE_TO_KEY.get(keycode & 0x00ff, '')
    modval = keycode & 0x1f00
    if modval in _MOD_VALUE_TO_KEY:
        return f"{_MOD_VALUE_TO_KEY[modval]}({contained})"
    table = _RIGHT_MOD_V2K if (modval & _MOD_CODES['QK_RMODS_MIN']) else _LEFT_MOD_V2K
    enabled = [name for val, name in table.items() if (val & modval) == val]
    return '('.join(enabled) + '(' + contained + ')' * len(enabled)


def _advanced_keycode_to_string(byte):
    """Port of advancedKeycodeToString."""
    pairs = []
    for a, b in [('_QK_MODS', '_QK_MODS_MAX'), ('_QK_MOD_TAP', '_QK_MOD_TAP_MAX'),
                 ('_QK_LAYER_TAP', '_QK_LAYER_TAP_MAX'), ('_QK_LAYER_MOD', '_QK_LAYER_MOD_MAX'),
                 ('_QK_TO', '_QK_TO_MAX'), ('_QK_MOMENTARY', '_QK_MOMENTARY_MAX'),
                 ('_QK_DEF_LAYER', '_QK_DEF_LAYER_MAX'), ('_QK_TOGGLE_LAYER', '_QK_TOGGLE_LAYER_MAX'),
                 ('_QK_ONE_SHOT_LAYER', '_QK_ONE_SHOT_LAYER_MAX'),
                 ('_QK_ONE_SHOT_MOD', '_QK_ONE_SHOT_MOD_MAX'),
                 ('_QK_LAYER_TAP_TOGGLE', '_QK_LAYER_TAP_TOGGLE_MAX'),
                 ('_QK_KB', '_QK_KB_MAX'), ('_QK_MACRO', '_QK_MACRO_MAX')]:
        if a in B and b in B:
            pairs.append((B[a], a)); pairs.append((B[b], b))

    last_range = None; last_value = -1
    for i in range(0, len(pairs), 2):
        if pairs[i][0] <= byte <= pairs[i + 1][0]:
            last_range = pairs[i][1]; last_value = pairs[i][0]

    if last_range == '_QK_MODS':
        return _top_level_mod_to_string(byte)

    # topLevelValueToMacro: byte value of each range -> macro name (LT, MO, ...)
    macro_name = {B[rng]: name for name, rng in _RANGE.items()}.get(last_value)
    if macro_name is None:
        return None
    hr = macro_name + '('
    remainder = byte & ~last_value
    if last_range in ('_QK_KB', '_QK_MACRO'):
        hr += str(byte - last_value) + ')'
    elif last_range in ('_QK_MOMENTARY', '_QK_DEF_LAYER', '_QK_TOGGLE_LAYER',
                        '_QK_ONE_SHOT_LAYER', '_QK_LAYER_TAP_TOGGLE', '_QK_TO'):
        hr += str(remainder) + ')'
    elif last_range == '_QK_LAYER_TAP':
        layer = remainder >> 8; kc = _BYTE_TO_KEY.get(remainder & 0xff, '')
        hr += f"{layer},{kc})"
    elif last_range == '_QK_ONE_SHOT_MOD':
        hr += _mod_value_to_string(remainder) + ')'
    elif last_range == '_QK_LAYER_MOD':
        mask = B['_QK_LAYER_MOD_MASK']; shift = (mask + 1).bit_length() - 1
        layer = remainder >> shift; modv = remainder & mask
        hr += f"{layer},{_mod_value_to_string(modv)})"
    elif last_range == '_QK_MOD_TAP':
        modv = (remainder >> 8) & 0x1f; kc = _BYTE_TO_KEY.get(remainder & 0xff, '')
        hr += f"{_mod_value_to_string(modv)},{kc})"
    else:
        return None
    return hr


def byte_to_code(byte):
    """VIA getCodeForByte. Returns a code string; raw hex for unknown bytes."""
    kc = _BYTE_TO_KEY.get(byte)
    if kc and not kc.startswith('_QK'):
        return kc
    if _is_layer_key(byte):
        c = _code_for_layer_byte(byte)
        if c is not None:
            return c
    adv = _advanced_keycode_to_string(byte)
    if adv is not None:
        return adv
    return '0x' + format(byte, 'x')

# ========================================================================
# HID protocol + CLI
# ========================================================================
#!/usr/bin/env python3
"""aks068 — load/save VIA keymaps on the Attack Shark / Ajazz AKS068 keyboard.

This keyboard runs a buggy QMK-derived firmware: the bulk DYNAMIC_KEYMAP_SET_BUFFER
command (0x13) that usevia.app uses for Import is broken, so the website cannot
load exported layouts. This tool sidesteps that bug:

  * read  keymap via DYNAMIC_KEYMAP_GET_BUFFER (0x12)   -- works in bulk
  * write keymap via DYNAMIC_KEYMAP_SET_KEYCODE (0x05)  -- one key at a time

It reads and writes the standard VIA export format ({name, vendorProductId,
macros, layers, encoders}), so you keep editing visually on usevia.app and use
this tool only for the load/save the website can't do.

Commands:
  devices                 list matching keyboards
  save   -f FILE          read keymap from keyboard -> VIA json file
  load   -f FILE          write VIA json file -> keyboard (per-key)
  load   -f FILE --dry-run   show what would change, write nothing

Safety: load auto-backs-up the current keymap first, writes only keys that
differ, then reads everything back and verifies. Only ever sends keymap
read/write commands -- never reset/bootloader/bulk-write.
"""



VID = 0x320F
PID_USB = 0x5055
PID_24G = 0x5088
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE = 0x61
MSG_LEN = 32

# VIA command ids
CMD_GET_PROTOCOL_VERSION = 0x01
CMD_GET_LAYER_COUNT = 0x11
CMD_GET_BUFFER = 0x12   # dynamic_keymap_get_buffer  [cmd, off_hi, off_lo, len]
CMD_SET_KEYCODE = 0x05  # dynamic_keymap_set_keycode [cmd, layer, row, col, hi, lo]

ROWS, COLS = 8, 16
KEYS_PER_LAYER = ROWS * COLS  # 128


class Keyboard:
    def __init__(self, path):
        self.dev = hid.device()
        self.dev.open_path(path)

    def close(self):
        self.dev.close()

    def _xfer(self, payload, settle=0.02):
        self.dev.write(b'\x00' + bytes(payload) + bytes(MSG_LEN - len(payload)))
        if settle:
            time.sleep(settle)
        return bytes(self.dev.read(MSG_LEN, timeout_ms=1000))

    def protocol_version(self):
        r = self._xfer([CMD_GET_PROTOCOL_VERSION])
        return (r[1] << 8) | r[2]

    def layer_count(self):
        r = self._xfer([CMD_GET_LAYER_COUNT])
        return r[1]

    def get_buffer(self, offset, length):
        """Read `length` bytes from the keymap buffer at byte `offset`.
        Bounded to 28 bytes/packet (32 - 4 header)."""
        out = bytearray()
        while length > 0:
            chunk = min(28, length)
            r = self._xfer([CMD_GET_BUFFER, (offset >> 8) & 0xFF, offset & 0xFF, chunk])
            if r[0] != CMD_GET_BUFFER:
                raise IOError(f"get_buffer bad echo at offset {offset}: {list(r[:4])}")
            out += r[4:4 + chunk]
            offset += chunk
            length -= chunk
        return bytes(out)

    def read_keymap(self, layers):
        """Return list[layer] of list[128] keycode integers."""
        km = []
        for layer in range(layers):
            base = layer * KEYS_PER_LAYER * 2
            raw = self.get_buffer(base, KEYS_PER_LAYER * 2)
            km.append([(raw[i] << 8) | raw[i + 1] for i in range(0, len(raw), 2)])
        return km

    def set_keycode(self, layer, row, col, value):
        r = self._xfer([CMD_SET_KEYCODE, layer, row, col,
                        (value >> 8) & 0xFF, value & 0xFF])
        if r[0] != CMD_SET_KEYCODE:
            raise IOError(f"set_keycode bad echo L{layer} ({row},{col}): {list(r[:6])}")
        return (r[4] << 8) | r[5]


def find_devices(pid=None):
    out = []
    for d in hid.enumerate(VID, 0):
        if d['usage_page'] == RAW_USAGE_PAGE and d['usage'] == RAW_USAGE:
            if pid is None or d['product_id'] == pid:
                out.append(d)
    return out


def pick_device(pid):
    devs = find_devices(pid)
    if not devs:
        sys.exit("error: no AKS068 raw-HID interface found "
                 "(is the keyboard connected in the right mode?)")
    if len(devs) > 1:
        sys.exit(f"error: {len(devs)} matching interfaces found; disconnect extras "
                 "or this tool needs a serial selector (none expose a serial).")
    return devs[0]['path']


# ----------------------------------------------------------------- file format
def keymap_to_via(km, name, vendor_product_id, macros=None, encoders=None):
    return {
        "name": name,
        "vendorProductId": vendor_product_id,
        "macros": macros if macros is not None else [""] * 16,
        "layers": [[byte_to_code(b) for b in layer] for layer in km],
        "encoders": encoders if encoders is not None else [],
    }


def via_to_keymap(doc):
    km = []
    for li, layer in enumerate(doc["layers"]):
        if len(layer) != KEYS_PER_LAYER:
            raise ValueError(f"layer {li} has {len(layer)} keys, expected {KEYS_PER_LAYER}")
        km.append([code_to_byte(c) for c in layer])
    return km


def idx_to_rc(i):
    return divmod(i, COLS)


# ----------------------------------------------------------------------- cmds
def cmd_devices(args):
    for d in find_devices():
        mode = {PID_USB: "USB/wired+BT", PID_24G: "2.4G dongle"}.get(d['product_id'], "?")
        print(f"VID=0x{d['vendor_id']:04x} PID=0x{d['product_id']:04x} ({mode})  "
              f"product={d['product_string']!r} path={d['path'].decode(errors='replace')}")
    if not find_devices():
        print("(no AKS068 raw-HID interfaces found)")


def cmd_save(args):
    kb = Keyboard(pick_device(args.pid))
    try:
        ver = kb.protocol_version()
        layers = kb.layer_count()
        print(f"protocol v{ver}, {layers} layers — reading keymap...")
        km = kb.read_keymap(layers)
    finally:
        kb.close()
    doc = keymap_to_via(km, args.name, (VID << 16) | args.pid)
    with open(args.file, "w") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
    total = sum(len(l) for l in km)
    print(f"saved {layers} layers ({total} keys) -> {args.file}")


def cmd_load(args):
    with open(args.file) as f:
        doc = json.load(f)
    target = via_to_keymap(doc)

    kb = Keyboard(pick_device(args.pid))
    try:
        ver = kb.protocol_version()
        layers = kb.layer_count()
        print(f"protocol v{ver}, {layers} layers on device; file has {len(target)} layers")
        if len(target) < layers:
            print(f"note: file has fewer layers ({len(target)}); "
                  f"only those will be written, deeper layers untouched")
        nlayers = min(layers, len(target))

        current = kb.read_keymap(layers)

        # diff
        changes = []  # (layer,row,col,old,new)
        for layer in range(nlayers):
            for i in range(KEYS_PER_LAYER):
                new = target[layer][i]
                old = current[layer][i]
                if new != old:
                    row, col = idx_to_rc(i)
                    changes.append((layer, row, col, old, new))

        print(f"{len(changes)} keys differ from current keymap")
        if args.dry_run:
            for layer, row, col, old, new in changes[:args.show]:
                print(f"  L{layer} ({row},{col}) {byte_to_code(old)} -> {byte_to_code(new)}")
            if len(changes) > args.show:
                print(f"  ... and {len(changes) - args.show} more")
            print("dry-run: nothing written")
            return

        if not changes:
            print("nothing to do — keymap already matches file")
            return

        # backup current state first
        if args.backup:
            bdoc = keymap_to_via(current, doc.get("name", "AKS068"),
                                 (VID << 16) | args.pid)
            with open(args.backup, "w") as f:
                json.dump(bdoc, f, indent=2); f.write("\n")
            print(f"backed up current keymap -> {args.backup}")

        # write per-key
        for n, (layer, row, col, old, new) in enumerate(changes, 1):
            got = kb.set_keycode(layer, row, col, new)
            if got != new:
                raise IOError(f"write mismatch L{layer} ({row},{col}): "
                              f"wrote 0x{new:04x} read 0x{got:04x}")
            if n % 25 == 0 or n == len(changes):
                print(f"  wrote {n}/{len(changes)}")

        # verify by full read-back
        print("verifying...")
        after = kb.read_keymap(layers)
        bad = []
        for layer in range(nlayers):
            for i in range(KEYS_PER_LAYER):
                if after[layer][i] != target[layer][i]:
                    row, col = idx_to_rc(i)
                    bad.append((layer, row, col,
                                after[layer][i], target[layer][i]))
        if bad:
            print(f"WARNING: {len(bad)} keys did not verify:")
            for layer, row, col, got, want in bad[:20]:
                print(f"  L{layer} ({row},{col}) got {byte_to_code(got)} "
                      f"want {byte_to_code(want)}")
            sys.exit(1)
        print(f"OK — {len(changes)} keys written and verified")
    finally:
        kb.close()


def main():
    p = argparse.ArgumentParser(description="Load/save VIA keymaps on the AKS068.")
    p.add_argument("--pid", type=lambda s: int(s, 0), default=PID_USB,
                   help="device product id (default 0x5055 USB/wired; 0x5088 = 2.4G)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("devices", help="list connected AKS068 interfaces")

    sp = sub.add_parser("save", help="read keymap from keyboard into a VIA json file")
    sp.add_argument("-f", "--file", required=True)
    sp.add_argument("--name", default="AKS068")

    lp = sub.add_parser("load", help="write a VIA json file to the keyboard")
    lp.add_argument("-f", "--file", required=True)
    lp.add_argument("--dry-run", action="store_true", help="show diff, write nothing")
    lp.add_argument("--show", type=int, default=40, help="max diff lines in dry-run")
    lp.add_argument("--backup", default=None,
                    help="write current keymap here before loading (recommended)")

    args = p.parse_args()
    {"devices": cmd_devices, "save": cmd_save, "load": cmd_load}[args.cmd](args)


if __name__ == "__main__":
    main()
