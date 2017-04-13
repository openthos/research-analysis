## SampleEnclave
```
/* Initialize the enclave:
 *   Step 1: try to retrieve the launch token saved by last transaction
 *   Step 2: call sgx_create_enclave to initialize an enclave instance
 *   Step 3: save the launch token if it is updated
*/
```

sgx_create_enclave
```c
extern "C" sgx_status_t sgx_create_enclave(const char *file_name, const int debug,
    sgx_launch_token_t *launch_token, int *launch_token_updated,
    sgx_enclave_id_t *enclave_id, sgx_misc_attribute_t *misc_attr)
```

enclave is the file of enclave, token 是从文件中读取的上一次保存的token(如果有)。
将enclave 打开后调用_create_enclave
```c
ret = _create_enclave(!!debug, fd, file, NULL, launch_token, launch_token_updated, enclave_id, misc_attr);
```
在这时候，会将之前从文件中读取的token用来验证是否可用。
最终会调用到__create_enclave
