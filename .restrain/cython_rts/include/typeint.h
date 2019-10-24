#pragma once
#include <stdint.h>
int64_t ptrtoint(void* ptr);
void* inttoptr(int64_t i);
int check_ptr_eq(void*, void*);