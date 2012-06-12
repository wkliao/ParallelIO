#ifndef __PIO_H_KINDS_INCLUDED_
#define __PIO_H_KINDS_INCLUDED_

// ---------------------------------------------------------------------
// Datatypes defined in pio_kinds.F90
// ---------------------------------------------------------------------

#include <stdint.h>
#include <mpi.h>

// ---------------------------------------------------------------------
// types for and sizes of the PIO Fortran derived types
// ---------------------------------------------------------------------

// sizeof( iosystem_desc_t)
typedef int pio_iosystem_desc_t;
extern const pio_iosystem_desc_t PIO_IOSYSTEM_DESC_NULL;
#define PIO_SIZE_IOSYSTEM_DESC  144

// sizeof( file_desc_t)
typedef void *pio_file_desc_t;
#define PIO_SIZE_FILE_DESC       24

// sizeof( io_desc_t)
typedef void *pio_io_desc_t;
#define PIO_SIZE_IO_DESC        472

// sizeof( var_desc_t)
typedef void *pio_var_desc_t;
#define PIO_SIZE_VAR_DESC        16

// PIO_OFFSET is the same type as MPI_Offset which is a typedef in C
#define PIO_Offset MPI_Offset

#endif // __PIO_H_KINDS_INCLUDED_