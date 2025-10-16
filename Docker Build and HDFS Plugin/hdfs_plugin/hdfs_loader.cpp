#include <SciDBAPI.h>
#include <hdfs.h>
#include <iostream>

using namespace scidb;

__attribute__((constructor))
void init_hdfs_plugin() {
    const char* namenode = "localhost";
    tPort port = 9000;

    std::cout << "[HDFS] Attempting connection to " << namenode << ":" << port << std::endl;

    hdfsFS fs = hdfsConnect(namenode, port);
    if (fs == nullptr)
        std::cerr << "[HDFS] Connection failed." << std::endl;
    else {
        std::cout << "[HDFS] Connected successfully!" << std::endl;
        hdfsDisconnect(fs);
    }
}
