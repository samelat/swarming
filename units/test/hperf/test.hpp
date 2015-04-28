#ifndef TEST_HPP
#define TEST_HPP

#include <cracker.hpp>

class Test : public Cracker {
public:
    Test(bp::object& callback) : Cracker(callback) {};

    Cracker::status_t login(const char * username, const char * password) override;
};

#endif