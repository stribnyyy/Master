//Директива == Библиотека
#include <iostream>
#include <ctime>
#include <string>
#include <bitset>

int main()
{
    uint8_t a = 0b10000000; // 0
    a = a << 1;
    std::cout << int(a) << " = " << std::bitset<sizeof(a)*8>(a) << std::endl;
    a = ~a;
    std::cout << int(a) << " = " << std::bitset<sizeof(a)*8>(a) << std::endl;
    return 0;
}