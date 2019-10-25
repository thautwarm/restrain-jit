import typing
call_record_t = typing.Tuple[int, ...]
call_records_t = typing.List[call_record_t]
fptr_addr = int

lineno_name = "restrain_lineno"
cont_name = "res_cont"
last_cont_name = "res_last_cont"
mangle_head = 'res_mg_'
gensym_head = "res_gen_"
typed_head = "res_tobe_typed_"
var_head = 'res_var_'
sym_head = "res_symbol_"
glob_head = "res_global_"
fn_head = "res_localfn_"
fn_addr = "res_address"
method_init_globals = "method_init_globals"
method_init_fptrs = "method_init_fptrs"

recorder = "restrain_call_recorder"
notifier = "restrain_recompilation_notifier"
method_init_recorder_and_notifier = "method_init_recorder_and_notifier"

Import = -10
TypeDecl = -5
Signature = -2
Customizable = 0
Normal = 5
Finally = 10

IDENTATION_SECTION = "    "
