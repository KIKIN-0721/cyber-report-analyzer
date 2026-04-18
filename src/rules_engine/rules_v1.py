# -*- coding: utf-8 -*-
from typing import Dict, Callable, Union

PASS = "Pass"
FAIL = "Fail"
CONDITIONAL_PASS = "Conditional Pass"
INVALID = "Invalid"

# ====================== 加密算法类规则 ======================
def check_T001_rsa_key_length(key_len: int) -> str:
    if not isinstance(key_len, int) or key_len < 0:
        return INVALID
    return PASS if key_len >= 2048 else FAIL

def check_T002_aes_key_length(key_len: int) -> str:
    if not isinstance(key_len, int) or key_len < 0:
        return INVALID
    return PASS if key_len >= 112 else FAIL

def check_T003_aes_iv(iv_type: str) -> str:
    if not isinstance(iv_type, str):
        return INVALID
    return PASS if iv_type == "Random" else FAIL

def check_T004_des(used: bool) -> str:
    if not isinstance(used, bool):
        return INVALID
    return PASS if not used else FAIL

def check_T005_hmac_md5(used: bool) -> str:
    if not isinstance(used, bool):
        return INVALID
    return PASS if not used else FAIL

def check_T006_aes_ecb(used: bool) -> str:
    if not isinstance(used, bool):
        return INVALID
    return PASS if not used else FAIL

def check_T007_md5(used: bool) -> str:
    if not isinstance(used, bool):
        return INVALID
    return PASS if not used else FAIL

def check_T008_sha1(used: bool) -> str:
    if not isinstance(used, bool):
        return INVALID
    return PASS if not used else FAIL

def check_T009_sha2(len_bits: int) -> str:
    if not isinstance(len_bits, int) or len_bits < 0:
        return INVALID
    return PASS if len_bits >= 224 else FAIL

def check_T010_sha3(len_bits: int) -> str:
    if not isinstance(len_bits, int) or len_bits < 0:
        return INVALID
    return PASS if len_bits >= 224 else FAIL

def check_T011_pbkdf2(iter_num: int) -> str:
    if not isinstance(iter_num, int) or iter_num < 0:
        return INVALID
    return PASS if iter_num >= 10000 else FAIL

def check_T012_hmac_sha1(used: bool) -> str:
    if not isinstance(used, bool):
        return INVALID
    return CONDITIONAL_PASS if used else PASS

def check_T013_hardcoded_key(used: bool) -> str:
    if not isinstance(used, bool):
        return INVALID
    return PASS if not used else FAIL

# ====================== CCK 规则 ======================
def check_T014_cck_random(generated_type: str) -> str:
    if not isinstance(generated_type, str):
        return INVALID
    return PASS if generated_type == "Random" else FAIL

def check_T015_cck_static(used: bool) -> str:
    if not isinstance(used, bool):
        return INVALID
    return PASS if not used else FAIL

# ====================== TLS & 通信 ======================
def check_T016_tls_version(version: str) -> str:
    if not isinstance(version, str):
        return INVALID
    return PASS if version in ["1.2", "1.3"] else FAIL

def check_T017_secure_channel(secure: bool) -> str:
    if not isinstance(secure, bool):
        return INVALID
    return PASS if secure else FAIL

def check_T018_local_connection(secure: bool) -> str:
    if not isinstance(secure, bool):
        return INVALID
    return PASS if secure else FAIL

def check_T019_cipher_suite(suite: str) -> str:
    if not isinstance(suite, str):
        return INVALID
    secure_list = ["GCM", "AES-GCM", "CHACHA20-POLY1305"]
    for s in secure_list:
        if s in suite:
            return PASS
    return FAIL

# ====================== 升级机制 ======================
def check_T020_update_sign(signed: bool) -> str:
    if not isinstance(signed, bool):
        return INVALID
    return PASS if signed else FAIL

def check_T021_auto_update(supported: bool) -> str:
    if not isinstance(supported, bool):
        return INVALID
    return PASS if supported else FAIL

def check_T022_local_update_check(checked: bool) -> str:
    if not isinstance(checked, bool):
        return INVALID
    return PASS if checked else FAIL

def check_T023_update_sign_alg(alg: str) -> str:
    if not isinstance(alg, str):
        return INVALID
    return PASS if "RSA" in alg and "SHA256" in alg else FAIL

def check_T024_local_update_secure(protected: bool) -> str:
    if not isinstance(protected, bool):
        return INVALID
    return PASS if protected else FAIL

# ====================== 密码 & 认证 ======================
def check_T025_preinstall_pwd(changed: bool) -> str:
    if not isinstance(changed, bool):
        return INVALID
    return PASS if changed else FAIL

def check_T026_pwd_length(length: int) -> str:
    if not isinstance(length, int) or length < 0:
        return INVALID
    return PASS if length >= 8 else FAIL

def check_T027_unique_key(unique: bool) -> str:
    if not isinstance(unique, bool):
        return INVALID
    return PASS if unique else FAIL

def check_T028_custom_pwd(supported: bool) -> str:
    if not isinstance(supported, bool):
        return INVALID
    return PASS if supported else FAIL

def check_T029_universal_pwd(exist: bool) -> str:
    if not isinstance(exist, bool):
        return INVALID
    return PASS if not exist else FAIL

# ====================== USB & 调试 ======================
def check_T030_usb_leak(leak: bool) -> str:
    if not isinstance(leak, bool):
        return INVALID
    return PASS if not leak else FAIL

def check_T031_debug_unique_auth(unique: bool) -> str:
    if not isinstance(unique, bool):
        return INVALID
    return PASS if unique else FAIL

def check_T032_ui_auth(enabled: bool) -> str:
    if not isinstance(enabled, bool):
        return INVALID
    return PASS if enabled else FAIL

def check_T033_debug_default_disabled(disabled: bool) -> str:
    if not isinstance(disabled, bool):
        return INVALID
    return PASS if disabled else FAIL

def check_T034_debug_protect(protected: bool) -> str:
    if not isinstance(protected, bool):
        return INVALID
    return PASS if protected else FAIL

# ====================== 访问控制 ======================
def check_T035_root_pwd(universal: bool) -> str:
    if not isinstance(universal, bool):
        return INVALID
    return PASS if not universal else FAIL

def check_T036_adb_ssh_restrict(restricted: bool) -> str:
    if not isinstance(restricted, bool):
        return INVALID
    return PASS if restricted else FAIL

def check_T037_account_isolation(isolated: bool) -> str:
    if not isinstance(isolated, bool):
        return INVALID
    return PASS if isolated else FAIL

# ====================== 安全存储 & 启动 ======================
def check_T038_secure_storage(mechanism: str) -> str:
    if not isinstance(mechanism, str):
        return INVALID
    safe = ["TEE", "Efuse", "FBE", "Secure"]
    # 精确匹配关键词，排除NonSecure等反例
    if any(s in mechanism for s in safe) and "Non" not in mechanism:
        return PASS
    return FAIL

def check_T039_secure_boot(enabled: bool) -> str:
    if not isinstance(enabled, bool):
        return INVALID
    return PASS if enabled else FAIL

def check_T040_selinux(mode: str) -> str:
    if not isinstance(mode, str):
        return INVALID
    return PASS if mode == "Enforcing" else FAIL

# ====================== 规则注册表（引擎自动加载） ======================
RULES_REGISTRY: Dict[str, Callable[..., Union[str, None]]] = {
    "T-001": check_T001_rsa_key_length,
    "T-002": check_T002_aes_key_length,
    "T-003": check_T003_aes_iv,
    "T-004": check_T004_des,
    "T-005": check_T005_hmac_md5,
    "T-006": check_T006_aes_ecb,
    "T-007": check_T007_md5,
    "T-008": check_T008_sha1,
    "T-009": check_T009_sha2,
    "T-010": check_T010_sha3,
    "T-011": check_T011_pbkdf2,
    "T-012": check_T012_hmac_sha1,
    "T-013": check_T013_hardcoded_key,
    "T-014": check_T014_cck_random,
    "T-015": check_T015_cck_static,
    "T-016": check_T016_tls_version,
    "T-017": check_T017_secure_channel,
    "T-018": check_T018_local_connection,
    "T-019": check_T019_cipher_suite,
    "T-020": check_T020_update_sign,
    "T-021": check_T021_auto_update,
    "T-022": check_T022_local_update_check,
    "T-023": check_T023_update_sign_alg,
    "T-024": check_T024_local_update_secure,
    "T-025": check_T025_preinstall_pwd,
    "T-026": check_T026_pwd_length,
    "T-027": check_T027_unique_key,
    "T-028": check_T028_custom_pwd,
    "T-029": check_T029_universal_pwd,
    "T-030": check_T030_usb_leak,
    "T-031": check_T031_debug_unique_auth,
    "T-032": check_T032_ui_auth,
    "T-033": check_T033_debug_default_disabled,
    "T-034": check_T034_debug_protect,
    "T-035": check_T035_root_pwd,
    "T-036": check_T036_adb_ssh_restrict,
    "T-037": check_T037_account_isolation,
    "T-038": check_T038_secure_storage,
    "T-039": check_T039_secure_boot,
    "T-040": check_T040_selinux,
}