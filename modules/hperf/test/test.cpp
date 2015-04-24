#include <boost/python.hpp>

using namespace boost::python;

class Cracker {
    str& callback;
    public:
        Cracker(str& cb) : callback(cb) {};
        void crack(list&, list&, list&);
};

void Cracker::crack(list& usernames, list& password, list& pairs) {
    //callback("samelat", "123456");

    std::cout << extract<std::string>(callback) << std::endl;
    //std::cout << extract<int>(usernames[0]) << std::endl;
}

BOOST_PYTHON_MODULE(test)
{
    class_<Cracker>("Cracker", init<str&>())
        .def("crack", &Cracker::crack);
}
