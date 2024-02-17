
CREATE TABLE car_sales (
    vehicle_id  String,
    created_at  Datetime,
    car_description  String,
    year  UInt32,
    brand  String,
    model  String,
    body_style  String,
    odometer  UInt32,
    transmission  String,
    fuel_type  String,
    engine_description  Nullable(String),
    engine_cylinders  Nullable(UInt32),
    engine_capacity  Nullable(UInt32),
    turbo  Nullable(UInt8),
    electric_capacity_kw  Nullable(UInt32),
    electric_range  Nullable(UInt32),
    price  Nullable(UInt32)
)
ENGINE = MergeTree
PRIMARY KEY (vehicle_id);

SELECT * FROM car_sales LIMIT 10;




