#include <typeint.h>

int64_t ptrtoint(void* ptr){
    return (int64_t) ptr;
}

void* inttoptr(int64_t i){
    return (void*) i;
}

int check_ptr_eq(void* a, void* b){
    return ptrtoint(a) == ptrtoint(b);
}