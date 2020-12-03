#define CAMERA_MODEL_M5STACK_PSRAM

#include "esp_camera.h"
#include "camera_pins.h"

#define FRAME_SIZE FRAMESIZE_QVGA
#define WIDTH 320
#define HEIGHT 240
#define BLOCK_SIZE 1
#define W (WIDTH / BLOCK_SIZE)
#define H (HEIGHT / BLOCK_SIZE)
#define BLOCK_DIFF_THRESHOLD 0.2
#define IMAGE_DIFF_THRESHOLD 0.1
#define DEBUG 1


//uint16_t proc_frame[H][W] = { 0 };
//uint16_t current_frame[H][W] = { 0 };
void find_max_pix();
bool convolve_gaussian_1D();
bool setup_camera(framesize_t);
bool capture_still();

void print_array(uint16_t myarray[H]);
void print_frame(uint16_t frame[H][W]);
int max_x = 0;
int max_y = 0;
uint16_t sum_proj[HEIGHT] = { 0 };
uint16_t sum_proj_conv[HEIGHT] = { 0 };

/**

*/
void setup() {
  Serial.begin(115200);
  Serial.println(setup_camera(FRAME_SIZE) ? "OK" : "ERR INIT");
}

/**

*/
void loop() {
  if (!capture_still()) {
    Serial.println("Failed capture");
    delay(3000);

    return;
  }

  convolve_gaussian_1D();


  //print_array(sum_proj_conv); 
  //Serial.println("=================");

  find_max_pix() ;
}


/**

*/
bool setup_camera(framesize_t frameSize) {
  camera_config_t config;

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_GRAYSCALE;
  config.frame_size = frameSize;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  bool ok = esp_camera_init(&config) == ESP_OK;

  sensor_t *sensor = esp_camera_sensor_get();
  sensor->set_framesize(sensor, frameSize);

  return ok;
}

/**
   Capture image and do down-sampling
*/
bool capture_still() {
  camera_fb_t *frame_buffer = esp_camera_fb_get();

  if (!frame_buffer)
    return false;

// set all 0s in current frame
  for (int y = 0; y < H; y++)
      sum_proj[y] = 0;

  // down-sample image in blocks
  for (uint32_t i = 0; i < WIDTH * HEIGHT; i++) {
    const uint16_t x = i % WIDTH;
    const uint16_t y = floor(i / WIDTH);
    const uint8_t pixel = frame_buffer->buf[i];
    sum_proj[y] += pixel;
  }


  return true;
}







/**
   For serial debugging
   @param frame
*/
void print_frame(uint16_t frame[H][W]) {
  for (int y = 0; y < H; y++) {
    for (int x = 0; x < W; x++) {
      int myval = 0;
      if (frame[y][x] >200) myval = frame[y][x];
      Serial.print(myval);
      Serial.print('\t');
    }

    Serial.println();
  }
}


/**
   For serial debugging
   @param frame
*/
void print_array(uint16_t myarray[H]) {
  for (int i = 0; i < H; i++) {
      int myval = 0;
      if (myarray[i] >200) myval = myarray[i];
      Serial.print(myval);
      Serial.print('\t');
    

    Serial.println();
  }
}


//  Different kernels:
// http://blog.dzl.dk/2019/06/08/compact-gaussian-interpolation-for-small-displays/
  
const float kernel[11] = {0.009300040045324049, 0.028001560233780885, 0.06598396774984912, 0.12170274650962626, 0.17571363439579307, 0.19859610213125314, 0.17571363439579, 0.12170274650962, 0.06598396774984, 0.028001560233785, 0.009300040045324};



/*
   Convolve the image with a gaussian and find the maximum position of the laserbeam
   Inspired by: http://www.songho.ca/dsp/convolution/convolution.html
*/




bool convolve_gaussian_1D() {
  // find center position of kernel (half of kernel size)
  int N = 11; // size kernel x
  for ( int i = 0; i < WIDTH; i++ )
  {
      sum_proj_conv[i] = 0;                       // set to zero before sum
      for ( int j = 0; j < N; j++ )
      {
          sum_proj_conv[i] += sum_proj[i - j] * kernel[j];    // convolve: multiply and accumulate
      }
  }
  return true;
}




/**
   Copy current frame to previous
*/
void find_max_pix() {
  int mymax = 0;
  int mymaxpos = -1;
  
  for (int y = 0; y < HEIGHT; y++) {
      if (sum_proj_conv[y]>mymax){
        mymax = sum_proj_conv[y];
        mymaxpos = y;
    }
  }
  Serial.print("My Max Val: ");
  Serial.print(mymax);
  Serial.print(" at pos: ");
  Serial.println(mymaxpos);  
}
