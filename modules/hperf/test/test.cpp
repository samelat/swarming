#include <boost/python.hpp>

using namespace boost::python;

class World {
    std::string s;
    public:
        World(std::string p1) : s(p1) {};
        void greet(object);
};

void World::greet(object o) {
    extract<dict> d(o);
    extract<std::string> s(d()["test"]);
    std::cout << s();
}

BOOST_PYTHON_MODULE(test)
{
    class_<World>("World", init<std::string>())
        .def("greet", &World::greet);
}
