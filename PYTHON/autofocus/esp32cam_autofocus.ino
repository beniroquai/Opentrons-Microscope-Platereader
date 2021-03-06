#define CAMERA_MODEL_M5STACK_PSRAM
#include <Adafruit_NeoPixel.h>

#ifdef __AVR__
#include <avr/power.h>
#endif

#include "esp_camera.h"
#include "camera_pins.h"

#define FRAME_SIZE FRAMESIZE_QVGA
#define WIDTH 320
#define HEIGHT 240
#define N_ROLLINGAVG 5
#define DEBUG 1
#define CAMERA_LED_GPIO 16
bool setup_camera(framesize_t);
bool capture_still();

void colorWipe(uint32_t c, uint8_t wait);

uint16_t sum_proj[HEIGHT] = { 0 };


// Add the neopixel strip for fluorescent illuminatino
Adafruit_NeoPixel strip = Adafruit_NeoPixel(5, CAMERA_LED_GPIO, NEO_GRB + NEO_KHZ800);

/**

*/
void setup() {
  Serial.begin(115200);
  Serial.println(setup_camera(FRAME_SIZE) ? "OK" : "ERR INIT");
 // init the LEDs 
    strip.begin();
  strip.show(); // Initialize all pixels to 'off'
  colorWipe(strip.Color(0, 0, 255), 50); // Blue

}

/**

*/
void loop() {
  if (!capture_still()) {
     delay(3000);
    return;
  }

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

  // setup the camera
  sensor_t *sensor = esp_camera_sensor_get();
  sensor->set_brightness(sensor, -2);     // -2 to 2
  sensor->set_contrast(sensor, 2);       // -2 to 2
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

  // down-sample image in blocks
  for (uint32_t i = 0; i < WIDTH * HEIGHT; i++) {
    const uint16_t x = i % WIDTH;
    const uint16_t y = floor(i / WIDTH);
    const uint8_t pixel = frame_buffer->buf[i];
    sum_proj[y] += (pixel/4); // avoid buffer overflows
  }

  // set all 0s in current frame
  for (int y =0; y<HEIGHT; y++){
    if (y%2){ // only pick every second pixel
      Serial.print(sum_proj[y]);
      Serial.print(",");  
    }
    sum_proj[y] = 0;
  }
  Serial.println(); 


  return true;
}




// Fill the dots one after the other with a color
void colorWipe(uint32_t c, uint8_t wait) {
  for (uint16_t i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, c);
    strip.show();
    delay(wait);
  }
}