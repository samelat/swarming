#include <boost/python.hpp>

#include <smb_mod.hpp>

using namespace boost::python;

BOOST_PYTHON_MODULE(smb)
{
    class_<SMB>("SMBCPP", init<std::string, unsigned short, unsigned int>())
        .def("try_login", &SMB::try_login)
        .def_readonly("CONNECTION_ERROR", &SMB::SMB_CONNECTION_ERROR)
		.def_readonly("TIMEOUT_ERROR"   , &SMB::SMB_TIMEOUT_ERROR)
		.def_readonly("LOGIN_SUCCESSFUL", &SMB::SMB_LOGIN_SUCCESSFUL)
		.def_readonly("LOGIN_FAILED"    , &SMB::SMB_LOGIN_FAILED)
    ;
}
