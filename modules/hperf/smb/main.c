#include <iostream>
#include <netinet/in.h>
#include <arpa/inet.h>

#include "smb_mod.hpp"

#include <vector>
#include <string>

using namespace std;

int main() {
	
	// vector<string> pass = {"192", "1725", "19289"};
    vector<string> pass = {"192", "1928", "19289"};
	
	SMB smb = SMB("192.168.2.206", 445, 8);
	
	for(vector<string>::iterator i = pass.begin(); i != pass.end(); i++) {
		if (smb.try_login("matt", *i) == SMB::SMB_LOGIN_SUCCESSFUL)
			cout << "Login\n";
		else
			cout << "Failure\n";
        cout << "\n";
	}
	
	return 0;
}
