from typing import Type, Any, get_origin, get_args
from pydantic import BaseModel


def create_skeleton(model_cls: Type[BaseModel]) -> dict[str, Any]:
    """
    Recursively creates a dictionary structure based on a Pydantic model.
    - Nested Models -> Nested Dictionaries
    - Lists -> Empty Lists []
    - Primitives/Enums -> None
    """
    skeleton = {}

    for name, field in model_cls.model_fields.items():
        # We need to find the actual type (handling Optional, List, etc.)
        field_type = field.annotation
        origin = get_origin(field_type)
        args = get_args(field_type)

        # 1. Handle Lists (e.g., List[Negocio])
        if origin is list or origin is list:
            # We return an empty list. The FSM logic must append items to it.
            skeleton[name] = []

        # 2. Handle Nested Pydantic Models
        # We check if it's a subclass of BaseModel.
        # We also need to handle Optional[Model] (Union[Model, NoneType])
        elif (isinstance(field_type, type) and issubclass(field_type, BaseModel)) or (
            origin is not None
            and any(isinstance(a, type) and issubclass(a, BaseModel) for a in args)
        ):
            # Extract the model class from Optional/Union if needed
            target_cls = field_type
            if origin is not None:
                # Find the arg that is a BaseModel
                for arg in args:
                    if isinstance(arg, type) and issubclass(arg, BaseModel):
                        target_cls = arg
                        break

            # Recurse!
            skeleton[name] = create_skeleton(target_cls)

        # 3. Primitives (str, int, float, Enums)
        else:
            # Use default if available, otherwise None
            skeleton[name] = None

    return skeleton
