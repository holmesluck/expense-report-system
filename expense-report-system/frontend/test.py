.background-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* Local image path - put your image in public/images/ */
  background-image: url('/images/bg.jpg');
  background-size: cover;        /* Cover entire screen */
  background-position: center;   /* Center the image */
  background-repeat: no-repeat;  /* Do not repeat */
  background-attachment: fixed;  /* Fixed background on scroll */
  z-index: -1;
}