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
	CameraId uint64
	PersonId uint64

	Camera Camera `json:"-" gorm:"primaryKey,foreignKey:CameraId"`
	Person Person `json:"-" gorm:"primaryKey,foreignKey:PersonId"`
}
