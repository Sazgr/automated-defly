#include <stddef.h>

void recolor(unsigned char* image, size_t size) {
    for (int i = 0; i < size; ++i) {
        if (image[3 * i + 1] >= 64 && image[3 * i + 2] >= 32 && (image[3 * i + 0] < 110 || image[3 * i + 0] > 120)) image[3 * i + 0] = 0;
    }
}

void aim(unsigned char* image, size_t height, size_t width, double* aim_x, double* aim_y) {
    *aim_x = 0.0;
    *aim_y = 0.0;
    int enemy_pixels = 0;
    for (int i = 0; i < height; ++i) {
        for (int j = 0; j < width; ++j) {
            if (image[3 * (i * width + j) + 1] >= 64 && image[3 * (i * width + j) + 2] >= 32 && image[3 * (i * width + j) + 0] == 0) {
                ++enemy_pixels;
                *aim_y += i - height / 2;
                *aim_x += j - width / 2;
            }
        }
    }
    if (enemy_pixels) {
        *aim_y /= enemy_pixels;
        *aim_x /= enemy_pixels;
    }
}