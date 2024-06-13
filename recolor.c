#include <stddef.h>
void recolor(unsigned char* image, size_t size) {
    for (int i = 0; i < size; ++i) {
        if (image[3 * i + 1] >= 64 && image[3 * i + 2] >= 32 && (image[3 * i + 0] < 110 || image[3 * i + 0] > 120)) image[3 * i + 0] = 0;
    }
}