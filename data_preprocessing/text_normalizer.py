"""
Vietnamese ASR Text Normalizer
Chuẩn hóa transcript tiếng Việt cho pipeline huấn luyện ASR.

Bao gồm:
- Unicode NFC normalization
- Lowercase
- Xóa URL, email, hashtag, @mention
- Xóa tag ASR (<unk>, <noise>...) và ký hiệu Wikipedia ([1], [2]...)
- Chuyển số → chữ viết tiếng Việt (số nguyên, thập phân, đơn vị đo)
- Từ điển viết tắt tiếng Việt (ko → không, dc → được...)
- Xóa dấu câu và ký tự đặc biệt
- Lọc tỉ lệ ký tự phi Việt
- Lọc transcript theo độ dài
"""

import re
import unicodedata

# ============================================================
# CONSTANTS
# ============================================================

# Vietnamese digits mapping
DIGITS = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]

# Vietnamese abbreviation dictionary (internet slang → full form)
ABBREVIATIONS = {
    "ko": "không",
    "k": "không",
    "dc": "được",
    "đc": "được",
    "dk": "được",
    "cx": "cũng",
    "cg": "cũng",
    "trc": "trước",
    "nc": "nói chuyện",
    "ntn": "như thế nào",
    "bn": "bao nhiêu",
    "vs": "với",
    "j": "gì",
    "r": "rồi",
    "lm": "làm",
    "mk": "mình",
    "ms": "mới",
    "ns": "nói",
    "nt": "nhắn tin",
    "ib": "nhắn tin",
    "ok": "ô kê",
    "nha": "nhé",
    "hen": "hẹn",
    "bik": "biết",
    "bt": "bình thường",
    "ck": "chồng",
    "vk": "vợ",
    "gato": "ghen ăn tức ở",
    "sp": "sản phẩm",
    "dt": "điện thoại",
    "sdt": "số điện thoại",
}

# Measurement unit dictionary (unit suffix → spoken Vietnamese)
UNITS = {
    "mg": "mi li gam",
    "ml": "mi li lít",
    "kg": "ki lô gam",
    "km": "ki lô mét",
    "cm": "xen ti mét",
    "mm": "mi li mét",
    "gb": "gi ga bai",
    "mb": "mê ga bai",
    "kb": "ki lô bai",
    "hz": "héc",
    "khz": "ki lô héc",
    "mhz": "mê ga héc",
    "ghz": "gi ga héc",
}

# Vietnamese character set (lowercase, including all diacritics + space)
VIETNAMESE_CHARS = set(
    "aăâbcdđeêghiklmnoôơpqrstuưvxy"
    "àảãáạằẳẵắặầẩẫấậèẻẽéẹềểễếệ"
    "ìỉĩíịòỏõóọồổỗốộờởỡớợùủũúụ"
    "ừửữứựỳỷỹýỵ "
)

# ============================================================
# NUMBER → VIETNAMESE WORDS
# ============================================================

def read_three_digits(num_str: str, has_higher: bool = False) -> str:
    """Read a 3-digit group into Vietnamese words."""
    num_str = num_str.zfill(3)
    h = int(num_str[0])
    t = int(num_str[1])
    u = int(num_str[2])

    words = []
    # Hundred
    if h > 0 or has_higher:
        words.append(DIGITS[h])
        words.append("trăm")

    # Ten
    if t == 0:
        if (h > 0 or has_higher) and u > 0:
            words.append("linh")
    elif t == 1:
        words.append("mười")
    else:
        words.append(DIGITS[t])
        words.append("mươi")

    # Unit
    if u > 0:
        if u == 1 and t > 1:
            words.append("mốt")
        elif u == 5 and t > 0:
            words.append("lăm")
        elif u == 4 and t > 1:
            words.append("tư")
        else:
            words.append(DIGITS[u])

    return " ".join(words)


def int_to_words(num: int) -> str:
    """Convert a non-negative integer to Vietnamese words."""
    if num == 0:
        return "không"

    units = ["", "nghìn", "triệu", "tỷ"]
    num_str = str(num)
    groups = []

    # Split into groups of 3 digits from right to left
    while num_str:
        groups.append(num_str[-3:])
        num_str = num_str[:-3]

    words = []
    for i, group in enumerate(groups):
        group_val = int(group)
        if group_val > 0 or (i == 0 and len(groups) == 1):
            has_higher = any(int(groups[j]) > 0 for j in range(i + 1, len(groups)))
            group_words = read_three_digits(group, has_higher=has_higher)

            # Determine unit
            if i > 0 and i % 3 == 0:
                unit = " ".join(["tỷ"] * (i // 3))
            else:
                unit = units[i] if i < len(units) else ""

            if unit:
                words.insert(0, f"{group_words} {unit}")
            else:
                words.insert(0, group_words)

    result = " ".join(words).strip()
    return re.sub(r'\s+', ' ', result)


# ============================================================
# NORMALIZATION SUB-STEPS
# ============================================================

def normalize_units(text: str) -> str:
    """Convert measurement units attached to numbers: '500mg' → '500 mi li gam'."""
    unit_pattern = re.compile(
        r'(\d+)\s*(' + '|'.join(re.escape(u) for u in sorted(UNITS.keys(), key=len, reverse=True)) + r')\b',
        re.IGNORECASE
    )

    def replace_unit(match):
        number_part = match.group(1)
        unit_key = match.group(2).lower()
        unit_text = UNITS.get(unit_key, unit_key)
        return f"{number_part} {unit_text}"

    return unit_pattern.sub(replace_unit, text)


def normalize_numbers(text: str) -> str:
    """Replace all numbers (integers and decimals) with Vietnamese words."""
    # 1. Decimal numbers: "1.5" or "2,5" → "một phẩy năm"
    decimal_pattern = re.compile(r'(\d+)[.,](\d+)')

    def replace_decimal(match):
        left = int_to_words(int(match.group(1)))
        right = int_to_words(int(match.group(2)))
        return f" {left} phẩy {right} "

    text = decimal_pattern.sub(replace_decimal, text)

    # 2. Integers: "2026" → "hai nghìn không trăm hai mươi sáu"
    integer_pattern = re.compile(r'\d+')

    def replace_integer(match):
        return f" {int_to_words(int(match.group(0)))} "

    text = integer_pattern.sub(replace_integer, text)
    return text


def expand_abbreviations(text: str) -> str:
    """Replace Vietnamese internet abbreviations with their full forms."""
    # Sort by length (longest first) to avoid partial replacements
    sorted_abbrs = sorted(ABBREVIATIONS.keys(), key=len, reverse=True)
    pattern = re.compile(
        r'\b(' + '|'.join(re.escape(a) for a in sorted_abbrs) + r')\b'
    )

    def replace_abbr(match):
        return ABBREVIATIONS.get(match.group(0), match.group(0))

    return pattern.sub(replace_abbr, text)


# ============================================================
# QUALITY FILTERS
# ============================================================

def non_viet_ratio(text: str) -> float:
    """Calculate the ratio of non-Vietnamese characters in text (0.0 to 1.0)."""
    if not text:
        return 1.0
    non_viet_count = sum(1 for c in text if c not in VIETNAMESE_CHARS)
    return non_viet_count / len(text)


def is_valid_transcript(text: str, min_length: int = 10, max_length: int = 1000,
                        max_non_viet_ratio: float = 0.3) -> bool:
    """
    Validate transcript quality based on baseline Zipformer-30M-RNNT-6000h filters:
    - Transcript length must be within [min_length, max_length] characters.
    - Ratio of non-Vietnamese characters must be <= max_non_viet_ratio.
    """
    if not text:
        return False
    if len(text) < min_length or len(text) > max_length:
        return False
    if non_viet_ratio(text) > max_non_viet_ratio:
        return False
    return True


# ============================================================
# MAIN NORMALIZATION PIPELINE
# ============================================================

def normalize_text(text: str) -> str:
    """
    Main Vietnamese ASR text normalization pipeline.
    Order of operations matters — do NOT rearrange steps without understanding dependencies.
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Unicode NFC Normalization (critical for Vietnamese diacritics)
    text = unicodedata.normalize('NFC', text)

    # 2. Lowercase
    text = text.lower()

    # 3. Remove URLs, emails (BEFORE punctuation stripping to avoid URL fragments)
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'\S+@\S+\.\S+', ' ', text)

    # 4. Remove Wikipedia reference tags: [1], [2], [cần dẫn nguồn]
    text = re.sub(r'\[\d+\]|\[cần dẫn nguồn\]', ' ', text)

    # 5. Remove ASR noise/special tags: <unk>, <noise>, <laughter>, [unknown], [applause]
    text = re.sub(r'<[^>]+>|\[[^\]]+\]', ' ', text)

    # 6. Remove emoji text patterns: :), ^^, =)), :D, :P, <3
    text = re.sub(r'[:;=]\s*[)(DPpOo3\|/\\]+|[\^]{2,}|[<>]3', ' ', text)

    # 7. Normalize measurement units BEFORE number conversion: "500mg" → "500 mi li gam"
    text = normalize_units(text)

    # 8. Convert numbers to spoken Vietnamese words: "2026" → "hai nghìn không trăm hai mươi sáu"
    text = normalize_numbers(text)

    # 9. Expand Vietnamese abbreviations: "ko" → "không", "dc" → "được"
    text = expand_abbreviations(text)

    # 10. Strip all remaining punctuation and special characters
    #     Keep only Unicode word characters (\w includes Vietnamese letters) and whitespace
    text = re.sub(r'[^\w\s]', ' ', text)
    #     Remove underscores (matched by \w but unwanted in ASR text)
    text = re.sub(r'_', ' ', text)

    # 11. Collapse multiple spaces into a single space
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    test_cases = [
        ("Tôi sinh năm 1995 tại Hà Nội.",
         "Expected: tôi sinh năm một nghìn chín trăm chín mươi lăm tại hà nội"),
        ("Mô hình đạt độ chính xác 98.5% trên tập test.",
         "Expected: ... chín mươi tám phẩy năm ... trên tập test"),
        ("Kinh Phật có 84000 pháp môn tu tập [1].",
         "Expected: ... tám mươi tư nghìn ... (no [1])"),
        ("Chào buổi sáng <noise> mọi người!",
         "Expected: chào buổi sáng mọi người"),
        ("Tập đoàn FPT được thành lập ngày 13-09-1988.",
         "Expected: ... mười ba chín một nghìn chín trăm tám mươi tám"),
        ("Tỷ lệ lạm phát là 3,45 phần trăm.",
         "Expected: ... ba phẩy bốn mươi lăm phần trăm"),
        ("Bạn dc ko? Trc đó mk cx lm r.",
         "Expected: bạn được không trước đó mình cũng làm rồi"),
        ("Liều dùng: 500mg paracetamol, uống 2 viên.",
         "Expected: liều dùng năm trăm mi li gam paracetamol uống hai viên"),
        ("Xem tại https://example.com/path?q=1 nhé!",
         "Expected: xem tại nhé (URL removed)"),
        ("Nặng 65kg, cao 170cm.",
         "Expected: nặng sáu mươi lăm ki lô gam cao một trăm bảy mươi xen ti mét"),
    ]

    print("=" * 60)
    print("Running Text Normalizer Tests")
    print("=" * 60)
    for raw, expected in test_cases:
        normalized = normalize_text(raw)
        valid = is_valid_transcript(normalized)
        print(f"  Raw:      {raw}")
        print(f"  Norm:     {normalized}")
        print(f"  Valid:    {valid}")
        print(f"  {expected}")
        print("-" * 60)
