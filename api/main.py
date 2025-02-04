from pydantic import BaseModel, Field
import sys
import json
import uvicorn
import pandas as pd
from loguru import logger
from typing import Optional, Literal
from fastapi import FastAPI, HTTPException

logger.add(sys.stdout, level="INFO")

app = FastAPI(
    title="Indian Vehicles API",
    summary="API for getting information about Indian vehicles",
    description="""
    This API provides information about Indian vehicles. It has two endpoints:
    1. /get_vehicle_info: Retrieve a vehicle record based on the specified type, brand, model, and variant.
    2. /get_vehicles_list: Retrieve a list of vehicles based on the specified type, brand, and model.

    Use the /get_vehicle_info endpoint to get detailed information about a specific vehicle.
    Use the /get_vehicles_list endpoint to get a list of unique vehicle brands, models, or variants based on the filters applied.

    Usage:
    - To get information about a specific vehicle, use the /get_vehicle_info endpoint with the following parameters:
        - vtype: The type of the vehicle, either 'Car' or 'Bike'.
        - brand: The brand of the vehicle. E.g., 'Toyota'.
        - model: The model of the vehicle. E.g., 'Camry'.
        - variant: The variant of the vehicle. E.g., 'Camry Elegance'.
    - To get a list of unique vehicle brands, models, or variants based on the filters applied, use the /get_vehicles_list endpoint with the following parameters:
        - vtype: The type of the vehicle, either 'Car' or 'Bike'.
        - brand: The brand of the vehicle. E.g., 'Toyota'.
        - model: The model of the vehicle. E.g., 'Camry'.

    The parameters are case-insensitive. The API will return a 404 error if no matching vehicle record is found.
    """,
    version="0.1",
    docs_url="/",
)


class Vehicle(BaseModel):
    VehicleType: str = Field(..., title="Vehicle Type",
                             description="The type of the vehicle, either 'Car' or 'Bike'")
    Brand: str = Field(..., title="Brand",
                       description="The brand of the vehicle")
    Model: str = Field(..., title="Model",
                       description="The model of the vehicle")
    Variant: str = Field(..., title="Variant",
                         description="The variant of the vehicle")
    Specs: dict = Field(..., title="Specs",
                        description="The specifications of the vehicle")


class VehicleList(BaseModel):
    Data: list = Field(..., title="Data",
                       description="A list of unique vehicle brands, models, or variants based on the filters applied.")

try:
    with open('data.json') as f:
        data = json.load(f)
        records = [
            {
                'Vehicle Type': vehicle,
                'Brand': brand,
                'Model': model,
                'Variant': variant,
                'Specs': data[vehicle][brand][model][variant]
            }
            for vehicle in data
            for brand in data[vehicle]
            for model in data[vehicle][brand]
            for variant in data[vehicle][brand][model]
        ]
        df = pd.DataFrame(records)
        logger.info("Data loaded successfully")
except FileNotFoundError:
    logger.error("data.json file not found")
    raise FileNotFoundError("data.json file not found")
except Exception as e:
    logger.error(f"Error loading data: {e}")
    raise e


@app.get('/get_vehicle_info', tags=['In-depth Vehicle Information'], response_model=Vehicle)
def get_vehicle(vtype: Literal['Car', 'Bike'], brand: str, model: str, variant: str):
    """
    Retrieve a vehicle record from the dataframe based on the specified type, brand, model, and variant.

    Args:
        vtype (Literal['Car', 'Bike']): The type of the vehicle, either 'Car' or 'Bike'.
        brand (str): The brand of the vehicle.
        model (str): The model of the vehicle.
        variant (str): The variant of the vehicle.

    Returns:
        dict: A dictionary representing the vehicle record.

    Raises:
        KeyError: If the specified key is not found in the dataframe.
        IndexError: If no matching vehicle record is found.
        Exception: For any other exceptions that may occur.
    """
    try:
        result = df[
            (df['Vehicle Type'].str.casefold() == vtype.strip().casefold()) &
            (df['Brand'].str.casefold() == brand.strip().casefold()) &
            (df['Model'].str.casefold() == model.strip().casefold()) &
            (df['Variant'].str.casefold() == variant.strip().casefold())
        ].to_dict(orient='records')[0]

        return Vehicle(
            VehicleType=result['Vehicle Type'],
            Brand=result['Brand'],
            Model=result['Model'],
            Variant=result['Variant'],
            Specs=result['Specs']
        )

    except KeyError as e:
        logger.error(f"KeyError: {e}")
        raise HTTPException(status_code=400, detail=f"KeyError: {e}")
    except IndexError as e:
        logger.error(f"IndexError: {e}")
        raise HTTPException(status_code=404, detail=f"IndexError: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")


@app.get('/get_vehicles_list', tags=['Vehicle List'], response_model=VehicleList)
def get_vehicles_list(vtype: Literal['Car', 'Bike'] = 'Car', brand: Optional[str] = None, model: Optional[str] = None,):
    """
    Retrieve a list of vehicles based on the specified type, brand, and model.
    Args:
        vtype (Literal['Car', 'Bike'], optional): The type of vehicle to filter by. Defaults to 'Car'. Returns all Brands of the specified type.
        brand (Optional[str], optional): The brand of the vehicle to filter by. Defaults to None. Returns all Models of the specified brand.
        model (Optional[str], optional): The model of the vehicle to filter by. Defaults to None. Returns all Variants of the specified model.
    Returns:
        List[str]: A list of unique vehicle brands, models, or variants based on the filters applied.
    Raises:
        KeyError: If a specified column does not exist in the DataFrame.
        IndexError: If the DataFrame index is out of range.
        Exception: For any other exceptions that may occur.
    """
    try:
        query = (df['Vehicle Type'].str.casefold() == vtype.casefold().strip())
        result = df[query]['Brand'].unique().tolist()
        if brand:
            query &= (df['Brand'].str.casefold() == brand.casefold().strip())
            result = df[query]['Model'].unique().tolist()
        if model:
            query &= (df['Model'].str.casefold() == model.casefold().strip())
            result = df[query]['Variant'].unique().tolist()

        return VehicleList(
            Data=result
        )
    except KeyError as e:
        logger.error(f"KeyError: {e}")
        raise HTTPException(status_code=400, detail=f"KeyError: {e}")
    except IndexError as e:
        logger.error(f"IndexError: {e}")
        raise HTTPException(status_code=404, detail=f"IndexError: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
