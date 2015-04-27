#include <boost/python.hpp>

#include <cracker.hpp>

using namespace boost::python;

class Cracker {
    PyObject * tmp;
    object pp;
    public:
        Cracker() {};
        void crack(list&, list&, list&);
        void test(object&);
        void test2(object);
        void test3();
};

void Cracker::crack(list& usernames, list& password, list& pairs) {
    //callback("samelat", "123456");

    //std::cout << extract<const char *>(callback) << std::endl;
    //std::cout << extract<int>(usernames[0]) << std::endl;
}

void Cracker::test(object& o) {
    tmp = o.ptr();
    std::cout << Py_REFCNT(tmp) << std::endl;
}

void Cracker::test3() {
    std::cout << Py_REFCNT(tmp) << std::endl;
}

void Cracker::test2(object o) {

    PyObject *po = o.ptr();
    std::cout << Py_REFCNT(po) << std::endl;
}

BOOST_PYTHON_MODULE(test)
{
    class_<Cracker>("Cracker", init<>())
        .def("crack", &Cracker::crack)
        .def("test", &Cracker::test)
        .def("test2", &Cracker::test2)
        .def("test3", &Cracker::test3);
}
