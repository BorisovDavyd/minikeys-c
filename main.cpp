#include <iostream>
#include <string>

int main(int argc, char** argv) {
    std::cout << "WARNING: mini-key format is deprecated and insecure.\n";
    std::cout << "Use for educational purposes only.\n";
    // TODO: Parse CLI options and invoke pipeline
    std::cout << "Arguments:";
    for(int i=0;i<argc;i++) std::cout << " " << argv[i];
    std::cout << std::endl;
    return 0;
}
