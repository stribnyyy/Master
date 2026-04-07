#include <iostream>
#include <string>
#include <cwctype>
#include <locale>
#include <vector>

// Преобразование wstring в UTF-8 string (работает на macOS/Linux/Windows)
std::string wstring_to_utf8(const std::wstring& wstr) {
    if (wstr.empty()) return std::string();
    // Получаем размер необходимого буфера
    int size_needed = std::wcstombs(nullptr, wstr.c_str(), 0);
    if (size_needed <= 0) return std::string();
    std::vector<char> buffer(size_needed + 1);
    std::wcstombs(buffer.data(), wstr.c_str(), size_needed);
    return std::string(buffer.data());
}

const std::wstring ALPHA_33 = L"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ";
const std::wstring ALPHA_32 = L"АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ";
const std::wstring ALPHA_44 = L"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ_0123456789";

int getIndex(wchar_t c, const std::wstring& alphabet) {
    size_t pos = alphabet.find(towupper(c));
    if (pos != std::wstring::npos) {
        return static_cast<int>(pos) + 1;
    }
    return -1;
}

std::wstring decryptXOR(const std::wstring& text, const std::wstring& key) {
    std::wstring result = L"";
    int keyIdx = 0;
    for (wchar_t c : text) {
        int p = getIndex(c, ALPHA_32);
        if (p == -1) p = 0; // для символов не из алфавита (пробел, ';' и т.д.)
        int k = getIndex(key[keyIdx % key.length()], ALPHA_32);
        int dec = p ^ k;
        if (dec == 0) dec = 32; // 0 отображается на букву 'Я' (индекс 32)
        result += ALPHA_32[dec - 1];
        keyIdx++;
    }
    return result;
}

int main() {
    // Устанавливаем локаль для корректной работы wcstombs
    std::setlocale(LC_ALL, "ru_RU.UTF-8");

    auto print = [](const std::wstring& wstr) {
        std::cout << wstring_to_utf8(wstr);
    };

    // Вариант 22
    print(L"=== 2. XOR Decryption (mod 2) - Variant 21 ===\n");
    std::wstring text21 = L"АИ ЧЦЦЭДТЖЦЭЛЗЫЕБОТСШЦ";
    std::wstring key21 = L"ресурс";
    print(L"Cipher:    ");
    print(text21);
    print(L"\nDecrypted: ");
    print(decryptXOR(text21, key21));
    print(L"\n");

    return 0;
}