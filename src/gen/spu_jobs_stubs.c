/* spu_jobs_stubs.c -- Default/fallback stubs for SPURS JobQueue jobs.
 * Provides weak symbols so the binary links even before all runtime dumps
 * are lifted. If a lifted job is present in spu_gen, it overrides these. */

#include "spu_context.h"
#include <stdio.h>

#define DEFINE_JOB_STUB(fp) \
    void job_##fp##_spu_recomp_register(void) __attribute__((weak)); \
    void job_##fp##_spu_recomp_register(void) {} \
    void job_##fp##_spu_func_00000000(spu_context* ctx) __attribute__((weak)); \
    void job_##fp##_spu_func_00000000(spu_context* ctx) { \
        (void)ctx; \
    }

DEFINE_JOB_STUB(0C7C7294454D5F48)
DEFINE_JOB_STUB(29F5F1C692D71C34)
DEFINE_JOB_STUB(3641D05246E29D20)
DEFINE_JOB_STUB(36DBDE8DC251D8C4)
DEFINE_JOB_STUB(56170BA0CB0F6E31)
DEFINE_JOB_STUB(6BA1F6CD43D6005F)
DEFINE_JOB_STUB(6D7C301B7D126EB9)
DEFINE_JOB_STUB(8AB0BC8AA6D7FFED)
DEFINE_JOB_STUB(A25123E89486EAD5)
DEFINE_JOB_STUB(BD259618FBD16916)
DEFINE_JOB_STUB(C06C06F3903D68BB)
DEFINE_JOB_STUB(CBC884B4E0F08A38)
DEFINE_JOB_STUB(D565C5363BCFA78C)
DEFINE_JOB_STUB(E0CC03D5957DAEAE)
DEFINE_JOB_STUB(FD1877A6E25051E0)
