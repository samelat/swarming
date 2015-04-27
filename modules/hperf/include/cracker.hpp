#ifndef CRACKER_HPP
#define CRACKER_HPP

#include <boost/python.hpp>

namespace bp = boost::python;

class Cracker {
    const bp::object callback;
    public:
        Cracker(bp::object& callback) : callback(callback) {};
        void crack(bp::list, bp::list, bp::list);

        virtual void login(const char * username, const char * password);
};

#endif