#include <Python.h>

#include "j2k.h"
#include "aw_j2k_errors.h"

static PyObject *AwareError;

#define RETURN_IF_ERR(retval, error_message)   \
  if (retval) {                                \
    PyErr_SetString(AwareError, error_message);  \
    return NULL;                               \
  }

static PyObject *
j2k_create(PyObject *self, PyObject *args)
{
  PyObject * result;
  int retval;
  aw_j2k_object *j2k_object;
  
  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  retval = aw_j2k_create(&j2k_object);
  RETURN_IF_ERR(retval, "aw_j2k_create returned an error code.");
  result = Py_BuildValue("i", j2k_object);
  return result;
}

static PyObject *
j2k_destroy(PyObject *self, PyObject *args)
{
  PyObject * result;
  int retval;
  aw_j2k_object *j2k_object;
  
  if (!PyArg_ParseTuple(args, "i", &j2k_object))
    return NULL;
  retval = aw_j2k_destroy(j2k_object);
  RETURN_IF_ERR(retval, "aw_j2k_destroy returned an error code.");
  j2k_object = NULL;
  result = Py_BuildValue("");
  return result;
}



static PyObject *
j2k_set_input_image(PyObject *self, PyObject *args)
{
  PyObject * result;
  int retval;
  aw_j2k_object *j2k_object;
  unsigned char* buffer;  // unsigned?
  unsigned long buffer_length;  // unsigned? long?

  if (!PyArg_ParseTuple(args, "is#", &j2k_object, &buffer, &buffer_length))
    return NULL;
  retval = aw_j2k_set_input_image(j2k_object, buffer, buffer_length);
  RETURN_IF_ERR(retval, "aw_j2k_set_input_image returned an error code.");
  result = Py_BuildValue("");
  return result;
}

static PyObject *
j2k_set_input_j2k_region_level(PyObject *self, PyObject *args)
{
  PyObject * result;
  int retval;
  aw_j2k_object *j2k_object;
  int x1, y1, x2, y2;

  if (!PyArg_ParseTuple(args, "iiiii", &j2k_object, &x1, &y1, &x2, &y2))
    return NULL;
  retval = aw_j2k_set_input_j2k_region_level(j2k_object, x1, y1, x2, y2);
  RETURN_IF_ERR(retval,
                "aw_j2k_set_input_j2k_region_level returned an error code.");
  result = Py_BuildValue("");
  return result;
}

static int FULL_XFORM_FLAG = 0;

static PyObject *
j2k_set_input_j2k_resolution_level(PyObject *self, PyObject *args)
{
  PyObject * result;
  int retval;
  aw_j2k_object *j2k_object;
  unsigned long int level; // why does this not work with int like in j2k.h??

  if (!PyArg_ParseTuple(args, "ik", &j2k_object, &level))
    return NULL;
  retval = aw_j2k_set_input_j2k_resolution_level(j2k_object, level,
						 FULL_XFORM_FLAG);
  RETURN_IF_ERR(retval,
                "aw_j2k_set_input_j2k_resolution_level returned an error code.");
  result = Py_BuildValue("");
  return result;
}

static PyObject *
j2k_set_output_com_image_size(PyObject *self, PyObject *args)
{
  PyObject * result;
  int retval;
  aw_j2k_object *j2k_object;
  int width, height;
  unsigned int preserve;

  if (!PyArg_ParseTuple(args, "iiiI", &j2k_object, &width, &height, &preserve))
    return NULL;
  retval = aw_j2k_set_output_com_image_size(j2k_object, 
					    height, width, preserve);
  RETURN_IF_ERR(retval,
                "aw_j2k_set_output_com_image_size returned an error code.");
  result = Py_BuildValue("");
  return result;
}

static PyObject *
j2k_get_output_image_raw(PyObject *self, PyObject *args)
{
  PyObject * result;
  int retval;
  aw_j2k_object *j2k_object;
  unsigned char *image_buffer;
  unsigned long int image_buffer_length;
  unsigned long int rows, cols, nChannels, bpp;

  image_buffer = NULL;

  if (!PyArg_ParseTuple(args, "i", &j2k_object))
    return NULL;
  retval = aw_j2k_get_output_image_raw(j2k_object,
				       &image_buffer, &image_buffer_length,
				       &rows, &cols,
				       &nChannels,
				       &bpp, 0);
  RETURN_IF_ERR(retval,
                "aw_j2k_get_output_image_raw returned an error code.");

  result = Py_BuildValue("iiiis#", rows, cols, nChannels, bpp,
                         image_buffer, image_buffer_length);

  aw_j2k_free(j2k_object, image_buffer);
  return result;
}

static PyObject *
j2k_get_input_image_info(PyObject *self, PyObject *args)
{
  PyObject * result;
  int retval;
  aw_j2k_object *j2k_object;
  unsigned long int rows, cols, nChannels, bpp;

  if (!PyArg_ParseTuple(args, "i", &j2k_object))
    return NULL;
  retval = aw_j2k_get_input_image_info(j2k_object, &rows, &cols, &bpp, 
                              &nChannels); 

  RETURN_IF_ERR(retval,
                "aw_j2k_get_input_image_info returned an error code.");

  result = Py_BuildValue("iiii", rows, cols, nChannels, bpp);
  return result;
}



static PyMethodDef AwareMethods[] = {
  {"j2k_create",  j2k_create, METH_VARARGS,
   "create a j2k_object."}, 
  {"j2k_destroy",  j2k_destroy, METH_VARARGS,
   "destroy a j2k_object."}, 
  {"j2k_set_input_image",  j2k_set_input_image, METH_VARARGS,
     ""}, 
  {"j2k_set_input_j2k_region_level",
   j2k_set_input_j2k_region_level, METH_VARARGS, ""}, 
  {"j2k_set_input_j2k_resolution_level",
   j2k_set_input_j2k_resolution_level, METH_VARARGS, ""}, 
  {"j2k_set_output_com_image_size",
   j2k_set_output_com_image_size, METH_VARARGS, ""}, 
  {"j2k_get_output_image_raw",
   j2k_get_output_image_raw, METH_VARARGS, ""}, 
  {"j2k_get_input_image_info",
   j2k_get_input_image_info, METH_VARARGS, ""}, 
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
init_aware(void)
{
  PyObject *m;

  m = Py_InitModule("_aware", AwareMethods);
  if (m == NULL)
    return;

   AwareError = PyErr_NewException("aware.error", NULL, NULL);
   Py_INCREF(AwareError);
   PyModule_AddObject(m, "error", AwareError);
}
