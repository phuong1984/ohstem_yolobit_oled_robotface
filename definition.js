const ColorRobotFace = '#44cbc6';

const ROBOTFACE_IMAGE_BASE =
  'https://raw.githubusercontent.com/phuong1984/ohstem_yolobit_oled_robotface/main/images';

const ROBOTFACE_EXPRESSIONS = [
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_01_neutral.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_NEUTRAL }, 'neutral'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_02_happy.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_HAPPY }, 'happy'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_03_laugh.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_LAUGH }, 'laugh'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_04_excited.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_EXCITED }, 'excited'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_05_love.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_LOVE }, 'love'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_06_wink.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_WINK }, 'wink'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_07_surprised.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_SURPRISED }, 'surprised'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_08_talk.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_TALK }, 'talk'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_09_sad.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_SAD }, 'sad'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_10_cry.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_CRY }, 'cry'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_11_angry.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_ANGRY }, 'angry'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_12_suspicious.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_SUSPICIOUS }, 'suspicious'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_13_sleepy.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_SLEEPY }, 'sleepy'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_14_sleep.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_SLEEP }, 'sleep'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_15_dizzy.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_DIZZY }, 'dizzy'],
  [{ src: ROBOTFACE_IMAGE_BASE + '/robot_face_16_error.jpg', width: 64, height: 32, alt: Blockly.Msg.ROBOTFACE_EXPR_ERROR }, 'error'],
];

const ROBOTFACE_ANIMATIONS = [
  ['blink', 'blink'],
  ['double_blink', 'double_blink'],
  ['wink', 'wink'],
  ['laugh', 'laugh'],
  ['surprise', 'surprise'],
  ['shake', 'shake'],
  ['nod', 'nod'],
  ['bounce', 'bounce'],
  ['look_around', 'look_around'],
  ['heartbeat', 'heartbeat'],
  ['dizzy', 'dizzy'],
  ['fall_asleep', 'fall_asleep'],
  ['wake_up', 'wake_up'],
];

const ROBOTFACE_LOOPS = [
  [Blockly.Msg.ROBOTFACE_LOOP_IDLE, 'idle'],
  [Blockly.Msg.ROBOTFACE_LOOP_TALK, 'talk'],
  [Blockly.Msg.ROBOTFACE_LOOP_HEARTBEAT, 'heartbeat'],
  [Blockly.Msg.ROBOTFACE_LOOP_LAUGH, 'laugh'],
  [Blockly.Msg.ROBOTFACE_LOOP_SOB, 'sob'],
];

const ROBOTFACE_DIRECTIONS = [
  [Blockly.Msg.ROBOTFACE_DIRECTION_CENTER, 'center'],
  [Blockly.Msg.ROBOTFACE_DIRECTION_LEFT, 'left'],
  [Blockly.Msg.ROBOTFACE_DIRECTION_RIGHT, 'right'],
  [Blockly.Msg.ROBOTFACE_DIRECTION_UP, 'up'],
  [Blockly.Msg.ROBOTFACE_DIRECTION_DOWN, 'down'],
  [Blockly.Msg.ROBOTFACE_DIRECTION_UP_LEFT, 'up_left'],
  [Blockly.Msg.ROBOTFACE_DIRECTION_UP_RIGHT, 'up_right'],
  [Blockly.Msg.ROBOTFACE_DIRECTION_DOWN_LEFT, 'down_left'],
  [Blockly.Msg.ROBOTFACE_DIRECTION_DOWN_RIGHT, 'down_right'],
];

const ROBOTFACE_BOOLEAN = [
  [Blockly.Msg.ROBOTFACE_ON, 'True'],
  [Blockly.Msg.ROBOTFACE_OFF, 'False'],
];

const ROBOTFACE_PLAY_MODES = [
  [Blockly.Msg.ROBOTFACE_PLAY_ONCE, 'once'],
  [Blockly.Msg.ROBOTFACE_PLAY_FOREVER, 'forever'],
];

function robotFaceDeclareImports() {
  Blockly.Python.definitions_['import_yolobit'] =
    'from yolobit import *';
  Blockly.Python.definitions_['import_robotface_machine'] =
    'from machine import Pin, SoftI2C';
  Blockly.Python.definitions_['import_robotface_ssd1306'] =
    'from ssd1306 import SSD1306_I2C';
  Blockly.Python.definitions_['import_robotface'] =
    'from robotface import RobotFace';
}

function robotFaceValue(block, name, fallback) {
  return Blockly.Python.valueToCode(block, name, Blockly.Python.ORDER_NONE) || fallback;
}

Blockly.Blocks['robotface_init'] = {
  init: function () {
    this.jsonInit({
      type: 'robotface_init',
      message0: Blockly.Msg.ROBOTFACE_INIT_MESSAGE,
      args0: [
        {
          type: 'field_number',
          name: 'FPS',
          value: 25,
          min: 1,
          max: 60,
          precision: 1,
        },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: ColorRobotFace,
      tooltip: Blockly.Msg.ROBOTFACE_INIT_TOOLTIP,
      helpUrl: '',
    });
  },
};

Blockly.Python['robotface_init'] = function (block) {
  robotFaceDeclareImports();
  const fps = block.getFieldValue('FPS');
  return 'oled = SSD1306_I2C(128, 64, SoftI2C(scl=Pin(pin19.pin), sda=Pin(pin20.pin)), addr=0x3C)\n' +
    'face = RobotFace(oled, fps=' + fps + ')\n';
};

Blockly.Blocks['robotface_expression'] = {
  init: function () {
    this.jsonInit({
      type: 'robotface_expression',
      message0: Blockly.Msg.ROBOTFACE_EXPRESSION_MESSAGE,
      args0: [
        {
          type: 'field_dropdown',
          name: 'EXPRESSION',
          options: ROBOTFACE_EXPRESSIONS,
        },
        {
          type: 'field_number',
          name: 'MS',
          value: 300,
          min: 0,
          precision: 1,
        },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: ColorRobotFace,
      tooltip: Blockly.Msg.ROBOTFACE_EXPRESSION_TOOLTIP,
      helpUrl: '',
    });
  },
};

Blockly.Python['robotface_expression'] = function (block) {
  const expression = block.getFieldValue('EXPRESSION');
  const ms = block.getFieldValue('MS');
  return 'face.expression("' + expression + '", ms=' + ms + ')\n';
};

Blockly.Blocks['robotface_play'] = {
  init: function () {
    this.jsonInit({
      type: 'robotface_play',
      message0: Blockly.Msg.ROBOTFACE_PLAY_MESSAGE,
      args0: [
        {
          type: 'field_dropdown',
          name: 'ANIMATION',
          options: ROBOTFACE_ANIMATIONS,
        },
        {
          type: 'field_dropdown',
          name: 'MODE',
          options: ROBOTFACE_PLAY_MODES,
        },
        {
          type: 'field_dropdown',
          name: 'WAIT',
          options: ROBOTFACE_BOOLEAN,
        },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: ColorRobotFace,
      tooltip: Blockly.Msg.ROBOTFACE_PLAY_TOOLTIP,
      helpUrl: '',
    });
  },
};

Blockly.Python['robotface_play'] = function (block) {
  const animation = block.getFieldValue('ANIMATION');
  const mode = block.getFieldValue('MODE');
  const wait = block.getFieldValue('WAIT');
  const repeat = mode === 'forever';
  return 'face.play("' + animation + '", wait=' + (repeat ? 'False' : wait) +
    ', loop=' + (repeat ? 'True' : 'False') + ')\n';
};

Blockly.Blocks['robotface_stop_animation'] = {
  init: function () {
    this.jsonInit({
      type: 'robotface_stop_animation',
      message0: Blockly.Msg.ROBOTFACE_STOP_ANIMATION_MESSAGE,
      args0: [],
      previousStatement: null,
      nextStatement: null,
      colour: ColorRobotFace,
      tooltip: Blockly.Msg.ROBOTFACE_STOP_ANIMATION_TOOLTIP,
      helpUrl: '',
    });
  },
};

Blockly.Python['robotface_stop_animation'] = function () {
  return 'face.stop_animation()\n';
};

Blockly.Blocks['robotface_loop'] = {
  init: function () {
    this.jsonInit({
      type: 'robotface_loop',
      message0: Blockly.Msg.ROBOTFACE_LOOP_MESSAGE,
      args0: [
        {
          type: 'field_dropdown',
          name: 'LOOP',
          options: ROBOTFACE_LOOPS,
        },
        {
          type: 'field_dropdown',
          name: 'ON',
          options: ROBOTFACE_BOOLEAN,
        },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: ColorRobotFace,
      tooltip: Blockly.Msg.ROBOTFACE_LOOP_TOOLTIP,
      helpUrl: '',
    });
  },
};

Blockly.Python['robotface_loop'] = function (block) {
  const loop = block.getFieldValue('LOOP');
  const on = block.getFieldValue('ON');
  return 'face.loop("' + loop + '", ' + on + ')\n';
};

Blockly.Blocks['robotface_talk_for'] = {
  init: function () {
    this.jsonInit({
      type: 'robotface_talk_for',
      message0: Blockly.Msg.ROBOTFACE_TALK_FOR_MESSAGE,
      args0: [
        {
          type: 'field_number',
          name: 'SECONDS',
          value: 3,
          min: 0,
          precision: 0.1,
        },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: ColorRobotFace,
      tooltip: Blockly.Msg.ROBOTFACE_TALK_FOR_TOOLTIP,
      helpUrl: '',
    });
  },
};

Blockly.Python['robotface_talk_for'] = function (block) {
  return 'face.talk_for(' + block.getFieldValue('SECONDS') + ')\n';
};

Blockly.Blocks['robotface_look'] = {
  init: function () {
    this.jsonInit({
      type: 'robotface_look',
      message0: Blockly.Msg.ROBOTFACE_LOOK_MESSAGE,
      args0: [
        {
          type: 'field_dropdown',
          name: 'DIRECTION',
          options: ROBOTFACE_DIRECTIONS,
        },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: ColorRobotFace,
      tooltip: Blockly.Msg.ROBOTFACE_LOOK_TOOLTIP,
      helpUrl: '',
    });
  },
};

Blockly.Python['robotface_look'] = function (block) {
  return 'face.look("' + block.getFieldValue('DIRECTION') + '")\n';
};

Blockly.Blocks['robotface_look_xy'] = {
  init: function () {
    this.jsonInit({
      type: 'robotface_look_xy',
      message0: Blockly.Msg.ROBOTFACE_LOOK_XY_MESSAGE,
      args0: [
        { type: 'input_value', name: 'X', check: 'Number' },
        { type: 'input_value', name: 'Y', check: 'Number' },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: ColorRobotFace,
      tooltip: Blockly.Msg.ROBOTFACE_LOOK_XY_TOOLTIP,
      helpUrl: '',
    });
  },
};

Blockly.Python['robotface_look_xy'] = function (block) {
  const x = robotFaceValue(block, 'X', '0');
  const y = robotFaceValue(block, 'Y', '0');
  return 'face.look_xy(' + x + ', ' + y + ')\n';
};

Blockly.Blocks['robotface_wait'] = {
  init: function () {
    this.jsonInit({
      type: 'robotface_wait',
      message0: Blockly.Msg.ROBOTFACE_WAIT_MESSAGE,
      args0: [
        {
          type: 'field_number',
          name: 'MS',
          value: 1000,
          min: 0,
          precision: 1,
        },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: ColorRobotFace,
      tooltip: Blockly.Msg.ROBOTFACE_WAIT_TOOLTIP,
      helpUrl: '',
    });
  },
};

Blockly.Python['robotface_wait'] = function (block) {
  return 'face.wait(' + block.getFieldValue('MS') + ')\n';
};

Blockly.Blocks['robotface_update'] = {
  init: function () {
    this.jsonInit({
      type: 'robotface_update',
      message0: Blockly.Msg.ROBOTFACE_UPDATE_MESSAGE,
      args0: [],
      previousStatement: null,
      nextStatement: null,
      colour: ColorRobotFace,
      tooltip: Blockly.Msg.ROBOTFACE_UPDATE_TOOLTIP,
      helpUrl: '',
    });
  },
};

Blockly.Python['robotface_update'] = function () {
  Blockly.Python.definitions_['import_robotface_time'] = 'import time';
  return 'face.update()\ntime.sleep_ms(1)\n';
};
