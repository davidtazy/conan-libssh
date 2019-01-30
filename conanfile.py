from conans import ConanFile, CMake, tools
import os

class LibsshConan(ConanFile):
    name = "libssh"
    version = "0.8.6"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Libssh here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = "zlib/1.2.11@conan/stable", "OpenSSL/1.1.1a@conan/stable"
    _source_subfolder = "sources_subfolder"
    _build_subfolder = "build_subfolder"

    def source(self):
        extracted_dir = "libssh-%s" % self.version
        archive_name = "%s.tar.xz" % extracted_dir
        source_url = "https://www.libssh.org/files/0.8/%s" % archive_name
        tools.get(source_url, sha1='2CB2775DCF2780520421A669EEBFE5862BA51D29'.lower() )
        os.rename(extracted_dir, self._source_subfolder)

        tools.replace_in_file("%s/CMakeLists.txt" % self._source_subfolder, "set(APPLICATION_NAME ${PROJECT_NAME})",
                              '''set(APPLICATION_NAME ${PROJECT_NAME})
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

        #fixme cmake doesnt see function...
        tools.replace_in_file("%s/ConfigureChecks.cmake" % self._source_subfolder,
            "check_function_exists(EVP_aes_128_ctr HAVE_OPENSSL_EVP_AES_CTR)",
            "set(HAVE_OPENSSL_EVP_AES_CTR 1)")

        #fixme findSSL link to libcrypto.a and not to libssl.a
        tools.replace_in_file("%s/src/CMakeLists.txt" % self._source_subfolder,
                              "${OPENSSL_CRYPTO_LIBRARY}",
                              "${CONAN_LIBS}")


    def configure(self):
        #c library
        del self.settings.compiler.libcxx

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = True
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()


    def package(self):
        self.copy("*.h", dst="include", src="%s/include" % self._source_subfolder)
        self.copy("*libssh.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["ssh"]

