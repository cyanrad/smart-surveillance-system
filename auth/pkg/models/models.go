package models

type Owner struct {
	ID   uint64 `gorm:"primaryKey"`
	Name string
}

type Camera struct {
	ID            uint64 `gorm:"primaryKey"`
	Is_Black_List bool

	OwnerId uint64
	Owner   Owner `json:"-" gorm:"foreignKey:OwnerId"`
}

type Person struct {
	ID    uint64 `gorm:"primaryKey"`
	Class string

	OwnerId uint64
	Owner   Owner `json:"-" gorm:"foreignKey:OwnerId"`
}

type Access struct {
	CameraId uint64 `gorm:"primaryKey;autoIncrement:false"`
	PersonId uint64 `gorm:"primaryKey;autoIncrement:false"`

	Camera Camera `json:"-" gorm:"foreignKey:CameraId"`
	Person Person `json:"-" gorm:"foreignKey:PersonId"`
}
