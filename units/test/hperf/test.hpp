#ifndef TEST_HPP
#define TEST_HPP

#include <cracker.hpp>

class Test : public Cracker {
public:
    Test(bp::object& callback) : Cracker(callback) {};
    void login(const char * username, const char * password) override;
};

#endif