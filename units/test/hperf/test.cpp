#include <iostream>

#include "test.hpp"

Cracker::status_t Test::login(const char * username, const char * password) {
    std::cout << "[!] " << username << " - " << password << std::endl;
    return Cracker::status_t::FAILED;
}