#include <stdlib.h>
#include <math.h>
#include <stdio.h>

#undef _DEBUG 
extern "C" 
{
#include <Python.h>
}

static PyObject *cpp_module_Cycle(PyObject *module, PyObject *args)
{
	PyObject *pymatrix=PyTuple_GetItem(args, 0);

	unsigned int i,j,k,dimension=PyObject_Size(pymatrix);
	double **mat=(double**)malloc(dimension*sizeof(double*));
	PyObject *string;
	PyObject *obj;
    PyObject *buf;

	for (i=0; i<dimension; ++i)
	{
		mat[i]=(double*)malloc(dimension*sizeof(double));
		string=PyList_GetItem(pymatrix, i);

		for (j=0; j<dimension; ++j)
		{
			obj=PyList_GetItem(string, j);
			mat[i][j]=PyFloat_AsDouble(obj);
		}
	}
	
	for (k=0; k<dimension; ++k)
	{
		for (i=0; i<dimension; ++i)
		{
			for (j=0; j<dimension; ++j)
			{
				mat[i][j]=1.0/( 1.0/mat[i][j] + 1.0/(mat[i][k]+mat[k][j]));
			}
		}
	}
	
	for (i=0; i<dimension; ++i)
	{
		PyObject *string = PyList_GetItem(pymatrix, i);

		for (j=0; j<dimension; ++j)
		{
			buf=PyFloat_FromDouble(mat[i][j]);
			PyList_SetItem(string, j, buf);
		}
	}

	Py_INCREF(Py_None);


	return Py_None;
}

PyMODINIT_FUNC PyInit_cpp_module()
{
	static PyMethodDef ModuleMethods[] =
	{
		{"Cycle", cpp_module_Cycle, METH_VARARGS,"Cycle(matrix):\n\n"},
		{NULL,NULL,NULL,NULL}
	};

	static PyModuleDef ModuleDef={PyModuleDef_HEAD_INIT,"cpp_module","cpp for task2",-1, ModuleMethods,NULL, NULL, NULL, NULL};
	PyObject *module=PyModule_Create(&ModuleDef);


	return module;
}