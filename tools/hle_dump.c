/* Print every firmware function the toolkit's HLE registers.
 *
 *   clang -O0 -I <psprecomp>/include tools/hle_dump.c <psprecomp>/build/libpsprecomp.a \
 *         -o /tmp/hle_dump && /tmp/hle_dump > hle.txt
 *
 * Output: "<NID>\t<library>\t<name>" per line, which tools/hle_coverage.py reads.
 */
#include <psprecomp/hle.h>
#include <stdio.h>

int main(void) {
    psp_hle_init();
    int n = 0;
    const psp_hle_entry *e = psp_hle_entries(&n);
    printf("# %d HLE entries\n", n);
    for (int i = 0; i < n; i++)
        printf("%08X\t%s\t%s\n", e[i].nid, e[i].lib ? e[i].lib : "?", e[i].name ? e[i].name : "-");
    return 0;
}
